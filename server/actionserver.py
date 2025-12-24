from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import hashlib

PASSWORD_SALT = "terminal-poker-2025"

def hash_password(password: str) -> str:
    return hashlib.sha256((PASSWORD_SALT + ":" + password).encode("utf-8")).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    return hash_password(password) == stored_hash

class ActionHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/ping":
            self._send_json(200, {
                "ok": True,
                "data": "pong"
            })
        elif self.path == "/players":
            self._send_json(200, {
                "ok": True,
                "data": self.server.game.players
            })
        elif self.path == "/table":
            self._send_json(200, {
                "ok": True,
                "data": {
                    "state": self.server.game.state_name,
                    "community_cards": self.server.game.community_cards,
                    "players": [
                        
                    ],
                    "blinds": [
                        {
                            "name": "Big Blind",
                            "blind": 1,
                            "table_id": 0
                        },
                        {
                            "name": "Small Blind",
                            "blind": 1,
                            "table_id": 1
                        }
                    ]
                }
            })
        else:
            self._send_json(404, {
                "ok": False,
                "error": "Not found"
            })

    def do_POST(self):
        def login():
            name = params.get("name", "")
            password = params.get("password", "")

            if not name or not password:
                self._send_json(400, {"ok": False, "error": "name and password are required"})
                return False

            try:
                with open("./.users.json", "r", encoding="utf-8") as users_file:
                    users_data = json.load(users_file)
            except FileNotFoundError:
                self._send_json(500, {"ok": False, "error": "users file not found"})
                return False

            users = users_data.get("existing", [])
            for user in users:
                if user.get("name") == name:
                    stored_hash = user.get("password_hash", "")
                    if verify_password(password, stored_hash):
                        return True
                    
            self._send_json(200, {"ok": True, "data": False})
            return False
        
        if self.path != "/action":
            self._send_json(404, {"ok": False, "error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "Invalid JSON"})
            return

        action_name = data.get("action")
        params = data.get("params", {})

        if action_name == "login":
            if login():
                self._send_json(200, {"ok": True, "data": True})
        elif action_name == "handshake":
            if login():
                table_id = params.get("table_id", "error")
                if table_id == "error":
                    self._send_json(400, {"ok": False, "error": "table_id is required"})
                    return
                for player in self.server.game.players:
                    if player.table_id == table_id:
                        self.server.game.handshake(table_id)
                        self._send_json(200, {"ok": True})
                        return
                self._send_json(400, {"ok": False, "error": "table_id is wrong"})
        elif action_name == "chat":
            if login():
                message = params.get("message", "error")
                if message == "error":
                    self._send_json(400, {"ok": False, "error": "message is required"})
                    return
                for player in self.server.game.players:
                    if player.table_id == table_id:
                        self.server.game.handshake(table_id)
                        self._send_json(200, {"ok": True})
                        return
                self._send_json(400, {"ok": False, "error": "table_id is wrong"})
        
        elif action_name == "say_hello":
            name = params.get("name", "World")
            result = f"Hello {name}!"
            self._send_json(200, {"ok": True, "result": result})
        elif action_name == "add":
            try:
                a = int(params.get("a", 0))
                b = int(params.get("b", 0))
            except ValueError:
                self._send_json(400, {"ok": False, "error": "a und b muessen int sein"})
                return
            
            result = a + b
            self._send_json(200, {"ok": True, "result": result})
        else:
            self._send_json(400, {"ok": False, "error": f"Unbekannte Aktion: {action_name}"})

def run(game):
    server_address = ("127.0.0.1", 8000)
    httpd = HTTPServer(server_address, ActionHandler)
    httpd.game = game
    httpd.serve_forever()