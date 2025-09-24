#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os

USERS_FILE = Path("./users.json")

active_users = {}
app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "Dealer"
CORS(app)

def read_file(path):
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def write_file(path, content):
    with path.open("w", encoding="utf-8") as file:
        json.dump(content, file, indent=4, ensure_ascii=False)

def main():
    os.system("clear")
    app.run(host="0.0.0.0", port=3000, debug=True)

@app.route("/")
def root():
    return app.send_static_file("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = read_file(USERS_FILE)
    if data["username"] in users:
        return jsonify({"success": False, "message": "Username existiert schon"})
    users[data["username"]] = data["password"]
    write_file(USERS_FILE, users)
    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = read_file(USERS_FILE)
    if users.get(data["username"]) == data["password"]:
        session["username"] = data["username"]
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Falsche Daten"})

@app.route("/me")
def me():
    return jsonify({"loggedIn": "username" in session, "username": session.get("username", "")})

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == "__main__":
    main()