from fastapi import FastAPI, Query, HTTPException
import uvicorn
import os

import poker

app = FastAPI(title="Terminal Poker")

@app.get("/")
def root():
    return {"ok": True}

@app.get("/hello")
def root():
    print("Hello World!")
    return {"ok": True, "message": "Hello World!"}

def run():
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    run()