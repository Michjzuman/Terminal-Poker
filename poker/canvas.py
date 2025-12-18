import curses
import time
from typing import Callable, Optional, Set, Union, Dict

KeyLike = Union[int, str]

class Canvas:
    def __init__(self, fps: int = 60, hold_window: float = 0.12, auto_clear: bool = False):
        self.fps = max(1, int(fps))
        self.hold_window = float(hold_window)
        self.auto_clear = bool(auto_clear)

        self._stdscr = None
        self._last_frame = 0.0
        self._last_seen: Dict[int, float] = {}
        self._just_pressed: Set[int] = set()
        self.colors: Dict[str, int] = {}

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

    def draw_pixel(self, x: int, y: int, ch: str, color: Optional[KeyLike] = "white") -> None:
        x = max(0, min(self.width - 1, x))
        y = max(1, min(self.height - 1, y))
        if not ch:
            return

        attr = None
        if color is not None:
            if isinstance(color, str):
                attr = self.colors.get(color.lower())
            else:
                try:
                    attr = curses.color_pair(int(color))
                except Exception:
                    attr = None

        try:
            if attr is not None:
                self._stdscr.attron(attr)
                self._stdscr.addch(y, x, ch[0])
                self._stdscr.attroff(attr)
            else:
                self._stdscr.addch(y, x, ch[0])
        except curses.error:
            pass
        
    def draw(self, x: int, y: int, chars: list) -> None:
        x = max(0, min(self.width - 1, x))
        y = max(1, min(self.height - 1, y))
        for yi, line in enumerate(chars):
            for xi, char in enumerate(line):
                self.draw_pixel(x + xi, y + yi, char)

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

            # In curses sind Spezialtasten ints (z.B. KEY_UP),
            # normale Buchstaben sind ord('a') etc.
            self._just_pressed.add(k)
            self._last_seen[k] = now

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

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

            curses.init_pair(1, curses.COLOR_RED, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)
            curses.init_pair(6, curses.COLOR_CYAN, -1)
            curses.init_pair(7, curses.COLOR_WHITE, -1)

            self.colors = {
                "red": curses.color_pair(1),
                "green": curses.color_pair(2),
                "yellow": curses.color_pair(3),
                "blue": curses.color_pair(4),
                "magenta": curses.color_pair(5),
                "cyan": curses.color_pair(6),
                "white": curses.color_pair(7),
            }

        self._last_seen.clear()
        self._just_pressed.clear()

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
