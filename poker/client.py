import requests

BASE_URL = "http://localhost:8000"

def get(path) -> str:
    url = f"{BASE_URL}/{path}"
    response = requests.get(url, timeout=5)
    return response.json()

def post(action: str, params: dict | None = None) -> dict:
    """
    Schickt eine Aktion an den HTTP-Aktionsserver und gibt die JSON-Antwort zurueck.
    """
    if params is None:
        params = {}

    url = f"{BASE_URL}/action"
    payload = {
        "action": action,
        "params": params
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=5
        )
    except requests.RequestException as e:
        # Hier kannst du Logging machen oder anders reagieren
        print(f"Fehler beim Request: {e}")
        return {"ok": False, "error": str(e)}

    # Optional: Statuscode pruefen
    if not response.ok:
        print(f"Server hat Fehlerstatus {response.status_code} zurueckgegeben")
        try:
            return response.json()
        except ValueError:
            return {"ok": False, "error": f"HTTP {response.status_code}", "raw": response.text}

    # JSON-Antwort parsen
    try:
        return response.json()
    except ValueError:
        return {"ok": False, "error": "Antwort ist kein gueltiges JSON", "raw": response.text}

def main():
    # Beispiel 1: say_hello
    result_hello = post("say_hello", {"name": "Micha"})
    print("say_hello ->", result_hello)

    # Beispiel 2: add
    result_add = post("add", {"a": 5, "b": 7})
    print("add ->", result_add)

    # Beispiel 3: unbekannte Aktion (zum Testen von Fehlerhandling)
    result_unknown = post("do_something_crazy", {"foo": "bar"})
    print("do_something_crazy ->", result_unknown)

if __name__ == "__main__":
    main()