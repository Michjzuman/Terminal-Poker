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
import uvicorn
import bcrypt
import asyncio
import json
import os

import poker

WAIT_UNITL_ROUND_START = 20

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

class Table:
    def __init__(self):
        global table_counter
        
        self.id: int = table_counter
        table_counter += 1
        
        self.game: poker.Game = None
        self.players: list[poker.Player] = []
        
        self.count_down = WAIT_UNITL_ROUND_START
        
        self.info = {}
        
    async def run(self):
        while self.game is None:
            if len(self.players) >= 2:
                self.count_down -= 1
                if self.count_down <= 0:
                    self.game = poker.Game(*self.players)
            await asyncio.sleep(1)
        
        self.game.deal_cards()
        
        while not self.game.finished:
            while True:
                print("a")
                
                self.info = {
                    "pool": self.game.pool,
                    "bet": self.game.bet,
                    "turn": self.game.turn,
                    "small_blind": self.game.small_blind,
                    "big_blind": self.game.big_blind,
                    "phase": self.game.phase,
                    "agressor": self.game.agressor,
                    "community_cards": self.game.community_cards,
                    "players": [
                        {
                            "name": player.name,
                            "bet": player.bet,
                            "money": player.money,
                            "is_in": player.is_in,
                            "possible_moves": player.possible_moves
                        }
                        for player in self.players
                    ],
                    "logs": self.game.logs
                }
                
                while True:
                    if self.game.play_move():
                        print("moved")
                        #print(self.game.players[0].possible_moves)
                        break
                    await asyncio.sleep(0.1)
                
                if self.game.agressor == self.game.turn:
                    break
                else:
                    await asyncio.sleep(1)
            
            self.game.next_phase()
            
            await asyncio.sleep(1)

class User(poker.Player):
    def __init__(self, name: str, password_hash: str):
        super().__init__(name, 100)
        self.password_hash: str = password_hash
        self.active: str = password_hash

tables: list[Table] = [Table() for _ in range(4)]

users: list[User] = []

register_requests: list[User] = []

data = {
    "tables": tables,
    "users": users,
    "register_requests": register_requests
}


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
                "active": table.game != None,
                "players": len(table.players),
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
    admin_password_hash = read_json_file(".admin-password-hash.json")["password"]
    if admin_password_hash and verify_password(body.password, admin_password_hash):
        return {"ok": True}
    else:
        return {"ok": False}

class LoginBody(PasswordBody):
    username: str = Field(..., min_length=1, max_length=64)
    
@app.post("/admin-approve-register-requests")
def admin_approve_register_requests(body: LoginBody):
    admin_password_hash = read_json_file(".admin-password-hash.json")["password"]
    if admin_password_hash and verify_password(body.password, admin_password_hash):
        for user in register_requests:
            if user.name == body.username:
                new_user = user
                users.append(new_user)
                register_requests.remove(new_user)
                return {"ok": True}
    return {"ok": False}

@app.post("/admin-reject-register-requests")
def admin_reject_register_requests(body: LoginBody):
    admin_password_hash = read_json_file(".admin-password-hash.json")["password"]
    if admin_password_hash and verify_password(body.password, admin_password_hash):
        for user in register_requests:
            if user.name == body.username:
                new_user = user
                register_requests.remove(new_user)
                return {"ok": True}
    return {"ok": False}

@app.post("/register")
def register(body: LoginBody):
    new_user = User(body.username, hash_password(body.password))
    for user in users + register_requests:
        if user.name == new_user.name:
            return {"ok": False}
    register_requests.append(new_user)
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

@app.post("/join_table")
def join_table(body: JoinTableBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")

    if table.game is not None:
        raise HTTPException(status_code=409, detail="Game already running")

    user = next((u for u in users if u.name == body.username), None)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if any(player.name == user.name for player in table.players):
        return {"ok": False}

    table.players.append(user)
    return {"ok": True}

@app.post("/my_cards")
def my_cards(body: JoinTableBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    user = next((u for u in users if u.name == body.username), None)
    
    if verify_password(body.password, user.password_hash):
        for player in table.players:
            cards = player.cards
            return {
                "ok": True,
                "cards": [
                    {
                        "rank": card.rank,
                        "suit": card.suit
                    }
                    for card in cards
                ]
            }
    
    return {"ok": False}

class MoveBody(JoinTableBody):
    move_type: str = Field(..., min_length=1, max_length=64)
    amount: int = Field(default=None, ge=0)

@app.post("/do_move")
def do_move(body: MoveBody):
    table = next((t for t in tables if t.id == body.table_id), None)
    user = next((u for u in users if u.name == body.username), None)
    
    try:
        move = poker.Move(
            poker.MoveType(body.move_type),
            body.amount
        )
        user.move = move
        
        print("move found!")
        
    except ValueError:
        return {"ok": False}

    return {"ok": True}

# === === === === === === === ===


def run():
    password = getpass("New Admin Password: ")
    write_json_file(".admin-password-hash.json", {"password": hash_password(password)})
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=6767,
        reload=False
    )

if __name__ == "__main__":
    run()
