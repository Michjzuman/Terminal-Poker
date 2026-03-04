from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os

import poker

app = FastAPI(title="Terminal Poker")

table_counter = 0

class Table:
    def __init__(self):
        global table_counter
        
        self.id: int = table_counter
        table_counter += 1
        
        self.game: poker.Game = ModuleNotFoundError

tables: list[Table] = [
    Table(),
    Table(),
    Table(),
    Table()
]

@app.get("/")
def root():
    return {"ok": True}

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
                "active": table.game != None,
                "id": table.id
            }
            for table in tables
        ]
    }

def run():
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    run()