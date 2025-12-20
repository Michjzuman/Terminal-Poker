from http.server import HTTPServer, BaseHTTPRequestHandler
import json

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
            self._send_json(200, {"ok": True, "msg": "pong"})
        else:
            self._send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
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

        if action_name == "say_hello":
            name = params.get("name", "World")
            result = f"Hello {name}!"
            self._send_json(200, {"ok": True, "result": result})
            return

        if action_name == "add":
            try:
                a = int(params.get("a", 0))
                b = int(params.get("b", 0))
            except ValueError:
                self._send_json(400, {"ok": False, "error": "a und b muessen int sein"})
                return

            result = a + b
            self._send_json(200, {"ok": True, "result": result})
            return

        self._send_json(400, {"ok": False, "error": f"Unbekannte Aktion: {action_name}"})

def run():
    server_address = ("127.0.0.1", 8000)
    httpd = HTTPServer(server_address, ActionHandler)
    print("Server laeuft auf http://127.0.0.1:8000 (CTRL+C zum Stoppen)")
    httpd.serve_forever()