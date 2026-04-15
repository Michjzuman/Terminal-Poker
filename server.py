#
# server.py
#
# Author:
# Micha Wüthrich
#
# Note:
# Run this file to host a server.
#


from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager, suppress
from pydantic import BaseModel, Field
from getpass import getpass
from datetime import datetime
import uvicorn
import bcrypt
import asyncio
import json
import os

import poker

WAIT_UNITL_ROUND_START = 7 # -> 20
HANDSHAKE_LIMIT = 60 # -> 5
MOVE_TIME_LIMIT = 30 # to do
USERS_LIST_FILE = ".server-users-list.json"
REGISTER_REQUESTS_FILE = ".server-register-requests.json"
ADMIN_PASSWORD_FILE = ".admin-password-hash.json"

DEFAULT_STARTING_MONEY = 100
ROUND_RESULT_SECONDS = 8
USERNAME_MAX_LENGTH = 10

table_counter = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.table_tasks = [
        asyncio.create_task(table.run(), name=f"table-{table.id}")
        for table in tables
    ]
    try:
        yield
    finally:
        for t in app.state.table_tasks:
            t.cancel()
        for t in app.state.table_tasks:
            with suppress(asyncio.CancelledError):
                await t

app = FastAPI(title="Terminal Poker", lifespan=lifespan)

def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def write_json_file(path: str, content):
    real_path = os.path.abspath(path)
    with open(real_path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

def read_json_file(path: str):
    try:
        real_path = os.path.abspath(path)
        with open(real_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return False

def serialize_card(card: poker.Card) -> dict:
    return {
        "rank": card.rank.value,
        "suit": card.suit.value,
    }

def serialize_user(user: "User") -> dict:
    return {
        "username": user.name,
        "password_hash": user.password_hash,
        "money": user.money,
    }

def deserialize_user(payload: dict) -> "User":
    return User(
        payload["username"],
        payload["password_hash"],
        payload.get("money", DEFAULT_STARTING_MONEY)
    )

def save_users():
    write_json_file(USERS_LIST_FILE, {
        "users": [serialize_user(user) for user in users]
    })

def save_register_requests():
    write_json_file(REGISTER_REQUESTS_FILE, {
        "register-requests": [serialize_user(user) for user in register_requests]
    })

def read_admin_password_hash() -> str | None:
    data = read_json_file(ADMIN_PASSWORD_FILE)
    if not data:
        return None
    return data.get("password")

def save_admin_password_hash(password_hash: str):
    write_json_file(ADMIN_PASSWORD_FILE, {"password": password_hash})

def seated_table_for_user(username: str):
    return next(
        (
            table
            for table in tables
            if any(player.name == username for player in table.players)
        ),
        None
    )

def serialize_hand(hand: poker.Hand | None) -> dict | None:
    if hand is None:
        return None
    return {
        "rank": hand.rank.name,
        "cards": [serialize_card(card) for card in hand.cards],
        "tiebreaker": list(hand.tiebreaker),
        "owner": hand.owner.name if hand.owner is not None else None,
    }

def serialize_pot(pot: dict) -> dict:
    return {
        "index": pot["index"],
        "amount": pot["amount"],
        "winners": [player.name for player in pot["winners"]],
        "winning_hand": serialize_hand(pot["winning_hand"]),
        "payouts": [
            {
                "player": player.name,
                "amount": amount,
            }
            for player, amount in pot["payouts"]
        ],
    }

def serialize_player_state(player: poker.Player) -> dict:
    to_call = 0
    minimum_raise_amount = 0
    maximum_raise_amount = 0
    is_turn = False

    if player.game is not None:
        to_call = player.game.to_call(player)
        minimum_raise_amount = player.game.minimum_raise_amount(player)
        maximum_raise_amount = max(0, player.money - to_call)
        is_turn = (
            not player.game.finished and
            not player.game.round_complete and
            0 <= player.game.turn < len(player.game.players) and
            player.game.players[player.game.turn] == player
        )

    return {
        "name": player.name,
        "bet": player.bet,
        "money": player.money,
        "is_in": player.is_in,
        "is_all_in": player.is_all_in,
        "is_turn": is_turn,
        "to_call": to_call,
        "minimum_raise_amount": minimum_raise_amount,
        "maximum_raise_amount": maximum_raise_amount,
        "possible_moves": [
            move.value
            for move in player.possible_moves
        ],
        "cards": " ".join([
            card.rank.value + card.suit.symbol
            for card in player.cards
        ]) if player.cards_revealed else None,
        "cards_revealed": player.cards_revealed,
        "total_contribution": player.total_contribution,
    }

class Table:
    def __init__(self):
        global table_counter
        
        self.id: int = table_counter
        table_counter += 1
        
        self.game: poker.Game = None
        self.players: list["User"] = []
        self.pending_leave: set[str] = set()
        
        self.count_down = WAIT_UNITL_ROUND_START
        self.turn_started_at: datetime | None = None
        
        self.info = {}

    def ready_players(self) -> list["User"]:
        now = datetime.now()
        result = []
        for player in self.players:
            if player.name in self.pending_leave:
                continue
            if not player.last_handshake:
                continue
            tid, last_handshake = player.last_handshake
            if tid != self.id:
                continue
            if (now - last_handshake).total_seconds() <= HANDSHAKE_LIMIT:
                result.append(player)
        return result

    def reset_after_hand(self):
        remaining_players = []
        for player in self.players:
            player.reset_for_round()
            player.game = None
            player.pending_leave = False
            if player.money > 0 and player.name not in self.pending_leave:
                remaining_players.append(player)
            else:
                player.last_handshake = ()

        self.players = remaining_players
        self.game = None
        self.count_down = WAIT_UNITL_ROUND_START
        self.turn_started_at = None
        self.pending_leave = set()
        self.info = {}

    def start_hand(self, players: list["User"]):
        for player in players:
            player.reset_for_round()
            player.pending_leave = False
            player.last_handshake = (self.id, datetime.now())
        self.game = poker.Game(*players)
        self.game.deal_cards()
        self.turn_started_at = datetime.now()

    def seat_count(self) -> int:
        return len(self.players)

    def connected_seat_count(self) -> int:
        return len(self.ready_players())

    def current_visible_pool(self) -> int:
        if self.game is None:
            return 0
        return self.game.pool + sum(player.bet for player in self.game.players)

    def current_result(self) -> dict:
        if self.game is None or not self.game.finished:
            return {}
        winners = self.game.winners
        winner_indexes = [
            self.game.players.index(winner)
            for winner in winners
            if winner is not None and winner in self.game.players
        ]
        return {
            "winner_indexes": winner_indexes,
            "winner_names": [
                winner.name
                for winner in winners
                if winner is not None
            ],
            "winning_hand": serialize_hand(self.game.pots[0]["winning_hand"]) if self.game.pots else None,
            "winning_hands": [
                serialize_hand(winner.best_hand)
                for winner in winners
                if winner is not None
            ],
            "payouts": [
                {
                    "player": payout_player.name,
                    "amount": amount,
                }
                for payout_player, amount in self.game.payouts
            ],
            "pots": [
                serialize_pot(pot)
                for pot in self.game.pots
            ],
        }
    
    def set_info(self, ended: bool = False):
        if self.game is None:
            self.info = {}
            return
        result = self.current_result()
        self.info = {
            "ended": ended,
            "finished": self.game.finished,
            "round_complete": self.game.round_complete,
            "pool": self.current_visible_pool(),
            "committed_pool": self.game.pool,
            "bet": self.game.bet,
            "turn": self.game.turn,
            "turn_name": (
                self.game.players[self.game.turn].name
                if 0 <= self.game.turn < len(self.game.players) else None
            ),
            "button_index": self.game.button_index,
            "small_blind_index": self.game.small_blind_index,
            "big_blind_index": self.game.big_blind_index,
            "small_blind": self.game.small_blind,
            "big_blind": self.game.big_blind,
            "phase": self.game.phase.value,
            "community_cards": [
                serialize_card(card)
                for card in self.game.community_cards
            ],
            "players": [
                serialize_player_state(player)
                for player in self.game.players
            ],
            "logs": self.game.logs,
            "winner": result.get("winner_indexes", []),
            "winner_names": result.get("winner_names", []),
            "winning_hand": result.get("winning_hand"),
            "winning_hands": result.get("winning_hands", []),
            "payouts": result.get("payouts", []),
            "pots": result.get("pots", []),
            "result": result,
        }
    
    async def run(self):
        while True:
            while self.game is None:
                ready_players = [
                    player for player in self.ready_players()
                    if player.money > 0
                ]
                if len(ready_players) >= 2:
                    self.count_down -= 1
                    if self.count_down <= 0:
                        self.start_hand(ready_players)
                        self.set_info()
                else:
                    self.count_down = WAIT_UNITL_ROUND_START
                await asyncio.sleep(1)

            while self.game is not None and not self.game.finished:
                if self.game.round_complete:
                    self.game.next_phase()
                    self.turn_started_at = datetime.now()
                    if self.game.finished:
                        break
                    continue

                self.set_info()

                current_player = self.game.players[self.game.turn]
                turn_age = 0.0
                if self.turn_started_at is not None:
                    turn_age = (datetime.now() - self.turn_started_at).total_seconds()

                if current_player.move is None and turn_age >= MOVE_TIME_LIMIT:
                    current_player.move = poker.Move(
                        poker.MoveType.CHECK
                        if poker.MoveType.CHECK in current_player.possible_moves else
                        poker.MoveType.FOLD
                    )

                if self.game.play_move():
                    self.turn_started_at = datetime.now()
                    if self.game.round_complete and not self.game.finished:
                        self.game.next_phase()
                        self.turn_started_at = datetime.now()
                    continue

                for player in self.game.players:
                    if not player.is_in:
                        continue
                    if not player.last_handshake:
                        continue
                    tid, last_handshake = player.last_handshake
                    diff = (datetime.now() - last_handshake).total_seconds()
                    if diff > HANDSHAKE_LIMIT or tid != self.id:
                        if player.move is None and player == self.game.players[self.game.turn]:
                            player.move = poker.Move(
                                poker.MoveType.CHECK
                                if poker.MoveType.CHECK in player.possible_moves else
                                poker.MoveType.FOLD
                            )

                await asyncio.sleep(0.1)

            save_users()
            self.set_info(True)
            await asyncio.sleep(ROUND_RESULT_SECONDS)
            self.reset_after_hand()

class User(poker.Player):
    def __init__(self, name: str, password_hash: str, money: int = DEFAULT_STARTING_MONEY):
        super().__init__(name, money)
        self.password_hash: str = password_hash
        self.last_handshake = ()
        self.pending_leave = False

tables: list[Table] = [Table() for _ in range(4)]

users: list[User] = []
users_list = read_json_file(USERS_LIST_FILE)
if users_list:
    users = [
        deserialize_user(user)
        for user in users_list["users"]
    ]
else:
    save_users()

register_requests: list[User] = []
register_requests_list = read_json_file(REGISTER_REQUESTS_FILE)
if register_requests_list:
    register_requests = [
        deserialize_user(user)
        for user in register_requests_list.get("register-requests", [])
    ]
else:
    save_register_requests()


# === === === === === === === ===
# --- GET --- ---

@app.get("/")
def root():
    return {"ok": True, "poker": True}

@app.get("/hello")
def hello():
    print("Hello World!")
    return {"ok": True, "message": "Hello World!"}

@app.get("/get_tables")
def get_tables():
    return {
        "ok": True,
        "tables": [
            {
                "id": table.id,
                "active": table.game is not None,
                "players": table.seat_count(),
                "ready_players": table.connected_seat_count(),
                "count_down": table.count_down,
                "info": table.info
            }
            for table in tables
        ]
    }

@app.get("/money")
def money():
    return {
        "ok": True,
        "players": {
            user.name: user.money
            for user in users
        }
    }

@app.get("/register-requests")
def show_register_requests():
    return {
        "ok": True,
        "register-requests": [
            user.name
            for user in register_requests
        ]
    }

# === === === === === === === ===
# --- POST -- ---

class PasswordBody(BaseModel):
    password: str = Field(..., min_length=1, max_length=200)

@app.post("/admin-login")
def admin_login(body: PasswordBody):
    admin_password_hash = read_admin_password_hash()
    if admin_password_hash and verify_password(body.password, admin_password_hash):
        return {"ok": True}
    else:
        return {"ok": False}

class LoginBody(PasswordBody):
    username: str = Field(..., min_length=1, max_length=64)

@app.post("/admin-approve-register-requests")
def admin_approve_register_requests(body: LoginBody):
    admin_password_hash = read_admin_password_hash()
    if admin_password_hash and verify_password(body.password, admin_password_hash):
        user = next((candidate for candidate in register_requests if candidate.name == body.username), None)
        if user is not None:
            users.append(user)
            register_requests.remove(user)
            save_users()
            save_register_requests()
            return {"ok": True}
    return {"ok": False}

@app.post("/admin-reject-register-requests")
def admin_reject_register_requests(body: LoginBody):
    admin_password_hash = read_admin_password_hash()
    if admin_password_hash and verify_password(body.password, admin_password_hash):
        user = next((candidate for candidate in register_requests if candidate.name == body.username), None)
        if user is not None:
            register_requests.remove(user)
            save_register_requests()
            return {"ok": True}
    return {"ok": False}

@app.post("/register")
def register(body: LoginBody):
    if len(body.username) > USERNAME_MAX_LENGTH:
        raise HTTPException(status_code=409, detail="Username too long")
    if " " in body.username:
        raise HTTPException(status_code=409, detail="Username contains spaces")
    new_user = User(body.username, hash_password(body.password))
    for user in users + register_requests:
        if user.name == new_user.name:
            return {"ok": False}
    register_requests.append(new_user)
    save_register_requests()
    return {"ok": True}

@app.post("/login")
def login(body: LoginBody):
    for user in users:
        if (
            body.username == user.name and
            verify_password(body.password, user.password_hash)
        ):
            return {"ok": True}
    return {"ok": False}

class JoinTableBody(LoginBody):
    table_id: int = Field(..., ge=0)

@app.post("/handshake")
def handshake(body: JoinTableBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    user = next((u for u in users if u.name == body.username), None)
    
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not any(player.name == user.name for player in table.players):
        raise HTTPException(status_code=409, detail="Player is not seated at this table")
    
    user.last_handshake = (body.table_id, datetime.now())
    return {"ok": True}

@app.post("/join_table")
def join_table(body: JoinTableBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    user = next((u for u in users if u.name == body.username), None)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    seated_table = seated_table_for_user(user.name)
    if seated_table is not None and seated_table.id != table.id:
        raise HTTPException(status_code=409, detail="Player already seated at another table")

    if any(player.name == user.name for player in table.players):
        user.last_handshake = (table.id, datetime.now())
        user.pending_leave = False
        return {"ok": True, "already_seated": True}

    if table.seat_count() >= 8:
        raise HTTPException(status_code=409, detail="Table is full")

    if table.game is not None:
        raise HTTPException(status_code=409, detail="Game already running")

    user.reset_for_round()
    user.pending_leave = False
    user.last_handshake = (table.id, datetime.now())
    table.players.append(user)
    return {"ok": True}

class LeaveTableBody(JoinTableBody):
    pass

@app.post("/leave_table")
def leave_table(body: LeaveTableBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    user = next((u for u in users if u.name == body.username), None)

    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    seated_user = next((player for player in table.players if player.name == user.name), None)
    if seated_user is None:
        raise HTTPException(status_code=409, detail="Player is not seated at this table")

    if table.game is not None and not table.game.finished and any(player.name == user.name for player in table.game.players):
        seated_user.pending_leave = True
        table.pending_leave.add(user.name)
        seated_user.last_handshake = ()
        seated_user.move = poker.Move(poker.MoveType.FOLD)
        return {"ok": True, "deferred": True}

    table.players = [
        player for player in table.players
        if player.name != user.name
    ]
    user.reset_for_round()
    user.pending_leave = False
    user.game = None
    user.last_handshake = ()
    table.pending_leave.discard(user.name)
    return {"ok": True, "deferred": False}

@app.post("/my_cards")
def my_cards(body: JoinTableBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    user = next((u for u in users if u.name == body.username), None)

    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not any(player.name == user.name for player in table.players):
        raise HTTPException(status_code=409, detail="Player is not seated at this table")

    return {
        "ok": True,
        "cards": [
            {
                "rank": card.rank.value,
                "suit": card.suit.value
            }
            for card in user.cards
        ]
    }

class MoveBody(JoinTableBody):
    move_type: str = Field(..., min_length=1, max_length=64)
    amount: int = Field(default=None, ge=0)

@app.post("/do_move")
def do_move(body: MoveBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    user = next((u for u in users if u.name == body.username), None)
    
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if table.game is None:
        raise HTTPException(status_code=409, detail="Game not running")

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not any(player.name == user.name for player in table.players):
        raise HTTPException(status_code=409, detail="Player is not seated at this table")

    if user.game != table.game:
        raise HTTPException(status_code=409, detail="Player is not part of the active hand")

    if table.game.finished or table.game.round_complete:
        raise HTTPException(status_code=409, detail="The current round is already complete")

    current_player = table.game.players[table.game.turn]
    if current_player != user:
        raise HTTPException(status_code=409, detail="It is not your turn")

    try:
        move = poker.Move(
            poker.MoveType(body.move_type),
            body.amount
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Move not legal")

    if move.type not in user.possible_moves:
        raise HTTPException(status_code=401, detail="Move not legal")

    if move.type.requires_amount:
        to_call = table.game.to_call(user)
        remaining_stack_after_call = max(0, user.money - to_call)
        minimum_raise_amount = table.game.minimum_raise_amount(user)

        if (
            move.amount is None or
            move.amount <= 0 or
            remaining_stack_after_call <= 0 or
            move.amount > remaining_stack_after_call or
            move.amount < minimum_raise_amount
        ):
            raise HTTPException(status_code=401, detail="Amount not legal")

    user.last_handshake = (body.table_id, datetime.now())
    user.move = move
    return {"ok": True}

# === === === === === === === ===


def run():
    if read_admin_password_hash() is None:
        password = getpass("Initial Admin Password: ")
        save_admin_password_hash(hash_password(password))
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=6767,
        reload=False
    )

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        exit()
