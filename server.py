from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager, suppress
from pydantic import BaseModel, Field
import uvicorn
import bcrypt
import asyncio
import os

import poker

WAIT_UNITL_ROUND_START = 5 #20

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
                self.info = {
                    "bet": self.game.bet,
                    "turn": self.game.turn,
                    "small_blind": self.game.small_blind,
                    "big_blind": self.game.big_blind,
                    "phase": self.game.phase,
                    "community_cards": self.game.community_cards,
                    "players": [
                        {
                            "name": player.name,
                            "money": player.money,
                            "is_is": player.is_in
                        }
                        for player in self.players
                    ]
                }
                while True:
                    if self.game.play_move():
                        print("moved")
                        break
                    await asyncio.sleep(0.1)
                
                self.game.your_turn()
                
                self.info["turn"] = self.game.turn
                
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

tables: list[Table] = [Table()]

users: list[User] = []


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
def get_tables():
    return {
        "ok": True,
        "players": {
            user.name: user.money
            for user in users
        }
    }


# === === === === === === === ===
# --- POST -- ---


class LoginBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=200)

@app.post("/register")
def register(body: LoginBody):
    new_user = User(body.username, hash_password(body.password))
    for user in users:
        if user.name == new_user.name:
            return {"ok": False}
    users.append(new_user)
    print(f"New User '{new_user.name}' Registered!")
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
        return {
            "ok": True,
            "cards": table
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
        move = poker.Move(body.move_type, body.amount)
        user.move = move
        print("move found!")
    except ValueError:
        return {"ok": False}

    table.players.append(user)
    return {"ok": True}

# === === === === === === === ===


def run():
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=6767,
        reload=False
    )

if __name__ == "__main__":
    run()
