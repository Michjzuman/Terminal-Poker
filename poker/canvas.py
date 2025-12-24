import curses
import re
import time
from typing import Callable, Set, Union, Dict, Tuple

import utils

KeyLike = Union[int, str]
RGBColor = Tuple[int, int, int]
RGB_PATTERN = re.compile(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", re.IGNORECASE)

class Canvas:
    def __init__(self, fps: int = 60, hold_window: float = 0.12, auto_clear: bool = False):
        self.fps = max(1, int(fps))
        self.hold_window = float(hold_window)
        self.auto_clear = bool(auto_clear)

        self._stdscr = None
        self._last_frame = 0.0
        self._last_seen: Dict[int, float] = {}
        self._just_pressed: Set[int] = set()

        self._color_pairs: Dict[RGBColor, int] = {}
        self._next_pair_id = 1
        self._palette: list[RGBColor] = []
        self._colors_enabled = False
        self._background_color = -1
        self._size: tuple[int, int] | None = None

    @property
    def width(self) -> int:
        h, w = self._stdscr.getmaxyx()
        return w

    @property
    def height(self) -> int:
        h, w = self._stdscr.getmaxyx()
        return h

    def clear(self) -> None:
        self._stdscr.erase()

    def draw_pixel(self, x: int, y: int, char: str, color = "rgb(255, 255, 255)") -> None:
        x = max(0, min(self.width - 1, x))
        y = max(1, min(self.height - 2, y))

        if not char:
            return

        attr = self._ensure_color(color)
        if attr:
            self._stdscr.attron(attr)
        self._stdscr.addch(y, x, char[0])
        if attr:
            self._stdscr.attroff(attr)
        
    def draw(self, chars: list, x: int, y: int) -> None:
        x = max(0, min(self.width - 1, x))
        y = max(1, min(self.height - 1, y))

        color = "white"
        for yi, line in enumerate(chars):
            xi = 0
            for char in line:
                if char in utils.COLORS:
                    color = utils.COLORS[char]
                else:
                    self.draw_pixel(x + xi, y + yi, char, color)
                    xi += 1

    def refresh(self) -> None:
        self._stdscr.refresh()

    def poll(self) -> None:
        """
        Liest alle Key-Events seit dem letzten Poll ein.
        Fuellt:
        - _last_seen: wann ein Key zuletzt kam
        - _just_pressed: Keys, die in diesem Poll neu reinkamen
        """
        self._just_pressed.clear()
        now = time.time()

        while True:
            k = self._stdscr.getch()
            if k == -1:
                break

            if k == curses.KEY_RESIZE:
                self._handle_resize()
                continue

            # In curses sind Spezialtasten ints (z.B. KEY_UP),
            # normale Buchstaben sind ord('a') etc.
            self._just_pressed.add(k)
            self._last_seen[k] = now

        self._check_resize()

        # Alte Eintraege ausduennen (optional)
        cutoff = now - max(self.hold_window * 4.0, 0.5)
        for k in list(self._last_seen.keys()):
            if self._last_seen[k] < cutoff:
                del self._last_seen[k]

    def pressed(self, key: KeyLike) -> bool:
        """
        "Key ist gedrueckt" = in den letzten hold_window Sekunden gesehen.
        """
        k = self._to_keycode(key)
        t = self._last_seen.get(k)
        if t is None:
            return False
        return (time.time() - t) <= self.hold_window

    def just_pressed(self, key: KeyLike) -> bool:
        """
        True nur in dem Frame/Poll, wo das Event reinkam.
        """
        k = self._to_keycode(key)
        return k in self._just_pressed

    def pressed_keys(self) -> Set[int]:
        """
        Aktuell "gedrueckt" nach hold_window-Regel.
        """
        now = time.time()
        return {k for k, t in self._last_seen.items() if (now - t) <= self.hold_window}

    def tick(self) -> None:
        """
        Frame pacing (FPS limit). Optional auto_clear.
        """
        if self.auto_clear:
            self.clear()

        target_dt = 1.0 / self.fps
        now = time.time()
        dt = now - self._last_frame
        sleep_time = target_dt - dt
        if sleep_time > 0:
            time.sleep(sleep_time)
        self._last_frame = time.time()

    def run(self, update_fn: Callable[["Canvas"], bool]) -> None:
        """
        Startet curses und ruft update_fn(canvas) pro Frame auf.
        update_fn muss True liefern um weiterzulaufen, False zum Beenden.
        """
        def _inner(stdscr):
            self._setup(stdscr)

            self._last_frame = time.time()
            while True:
                self.poll()

                if self.auto_clear:
                    self.clear()

                keep_going = update_fn(self)
                self.refresh()
                self.tick()

                if not keep_going:
                    break

        curses.wrapper(_inner)

    # ---------- Internals ----------

    def _setup(self, stdscr) -> None:
        self._stdscr = stdscr

        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()

        self._stdscr.keypad(True)
        self._stdscr.nodelay(True)   # getch() blockiert nicht
        self._stdscr.timeout(0)      # sofort zurueck

        self._last_seen.clear()
        self._just_pressed.clear()
        self._init_colors()
        self._size = self._stdscr.getmaxyx()

    def _init_colors(self) -> None:
        self._color_pairs.clear()
        self._next_pair_id = 1
        self._palette = []
        self._colors_enabled = False
        self._background_color = -1

        try:
            curses.start_color()
            self._colors_enabled = curses.has_colors()
        except curses.error:
            return

        try:
            curses.use_default_colors()
        except curses.error:
            self._background_color = 0

        if not self._colors_enabled:
            return

        self._palette = self._build_palette()

    def _build_palette(self) -> list[RGBColor]:
        max_colors = max(0, curses.COLORS)
        palette: list[RGBColor] = []
        for idx in range(min(max_colors, 256)):
            try:
                r, g, b = curses.color_content(idx)
                palette.append(self._scale_to_255(r, g, b))
            except curses.error:
                palette = [self._xterm_color_at(i) for i in range(min(max_colors, 256))]
                break

        if not palette and max_colors > 0:
            palette = [self._xterm_color_at(i) for i in range(min(max_colors, 256))]
        if not palette:
            palette = [utils.EXACT_COLORS.get("white", (255, 255, 255))]
        return palette

    def _check_resize(self) -> None:
        if self._stdscr is None:
            return

        actual = self._stdscr.getmaxyx()
        if self._size != actual:
            self._handle_resize(actual)

    def _handle_resize(self, new_size: tuple[int, int] | None = None) -> None:
        if self._stdscr is None:
            return

        target_size = new_size or self._stdscr.getmaxyx()
        if self._size == target_size:
            return

        try:
            curses.update_lines_cols()
        except curses.error:
            pass

        try:
            curses.resize_term(*target_size)
        except curses.error:
            pass

        try:
            self._stdscr.resize(*target_size)
        except curses.error:
            pass

        self._stdscr.clear()
        self._size = target_size

    def _scale_to_255(self, r: int, g: int, b: int) -> RGBColor:
        return (
            min(255, max(0, int(round(r * 255 / 1000)))),
            min(255, max(0, int(round(g * 255 / 1000)))),
            min(255, max(0, int(round(b * 255 / 1000)))),
        )

    def _ensure_color(self, color: Union[str, RGBColor]) -> int:
        if not self._colors_enabled:
            return 0

        rgb = self._to_rgb(color)
        key = tuple(rgb)

        cached = self._color_pairs.get(key)
        if cached is not None:
            return cached

        fg_index = self._nearest_palette_index(rgb)
        max_pairs = max(1, curses.COLOR_PAIRS)
        pair_id = min(self._next_pair_id, max_pairs - 1) or 1

        try:
            curses.init_pair(pair_id, fg_index, self._background_color)
            attr = curses.color_pair(pair_id)
        except curses.error:
            attr = 0

        self._color_pairs[key] = attr
        if self._next_pair_id < max_pairs - 1:
            self._next_pair_id += 1
        return attr

    def _nearest_palette_index(self, rgb: RGBColor) -> int:
        if not self._palette:
            return getattr(curses, "COLOR_WHITE", 0)

        r, g, b = rgb
        best_idx = 0
        best_dist = float("inf")
        for idx, (pr, pg, pb) in enumerate(self._palette):
            dist = (pr - r) ** 2 + (pg - g) ** 2 + (pb - b) ** 2
            if dist < best_dist:
                best_idx = idx
                best_dist = dist
        return best_idx

    def _to_rgb(self, color: Union[str, RGBColor]) -> RGBColor:
        if isinstance(color, (tuple, list)) and len(color) == 3:
            return tuple(self._clamp_channel(int(c)) for c in color)  # type: ignore[arg-type]

        if not isinstance(color, str):
            return utils.EXACT_COLORS.get("white", (255, 255, 255))

        c = color.strip().lower()
        if not c:
            return utils.EXACT_COLORS.get("white", (255, 255, 255))

        if c in utils.EXACT_COLORS:
            return utils.EXACT_COLORS[c]

        match = RGB_PATTERN.match(c)
        if match:
            return tuple(self._clamp_channel(int(v)) for v in match.groups())  # type: ignore[return-value]

        return utils.EXACT_COLORS.get("white", (255, 255, 255))

    def _clamp_channel(self, value: int) -> int:
        return max(0, min(255, value))

    def _xterm_color_at(self, index: int) -> RGBColor:
        base16 = [
            (0, 0, 0),
            (205, 0, 0),
            (0, 205, 0),
            (205, 205, 0),
            (0, 0, 238),
            (205, 0, 205),
            (0, 205, 205),
            (229, 229, 229),
            (127, 127, 127),
            (255, 0, 0),
            (0, 255, 0),
            (255, 255, 0),
            (92, 92, 255),
            (255, 0, 255),
            (0, 255, 255),
            (255, 255, 255),
        ]

        if index < len(base16):
            return base16[index]

        if index < 232:
            idx = index - 16
            r = idx // 36
            g = (idx % 36) // 6
            b = idx % 6
            levels = [0, 95, 135, 175, 215, 255]
            return (levels[r], levels[g], levels[b])

        level = 8 + 10 * (index - 232)
        return (level, level, level)

    def _to_keycode(self, key: KeyLike) -> int:
        if isinstance(key, int):
            return key
        if isinstance(key, str):
            if len(key) == 1:
                return ord(key)
            # Kleine convenience Aliases:
            k = key.lower().strip()
            if k == "up":
                return curses.KEY_UP
            if k == "down":
                return curses.KEY_DOWN
            if k == "left":
                return curses.KEY_LEFT
            if k == "right":
                return curses.KEY_RIGHT
        raise TypeError("key muss int, 1-char str oder Alias wie 'up' sein")
