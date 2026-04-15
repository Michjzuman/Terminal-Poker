#
# admin.py
#
# Author:
# Micha Wüthrich
#
# Note:
# Run this file to enter the poker server admin panel.
#


import play

def admin_panel_login_view(ui):
    pointer = 0
    error = ""
    text_inputs = {
        "Server Host": "",
        "Admin Password": ""
    }
    
    with play.cbreak_stdin():
        while True:
            ui.reset_text()
            
            ui.poker_logo(round(ui.w / 2) - 24, 3, play.UI.Color.RED)
            
            ui.label(error, 10, play.UI.Color.RED)
            
            for i, text_input in enumerate(text_inputs):
                ui.text_input(
                    text_inputs[text_input], pointer == i, 12 + 5 * i, text_input,
                    "Password" in text_input
                )
                    
            ui.menu(pointer - len(text_inputs), ["Done"], play.UI.Color.RED, 23)
            
            ui.draw("↑/↓: Move • ENTER: Confirm • ^C: Quit")
            
            
            while True:
                key = play.read_key()
                if key == "ESC":
                    return
                elif key == "UP":
                    pointer -= 1
                    pointer %= len(text_inputs) + 1
                    break
                elif (key == "ENTER") or (key == " " and pointer >= 1):
                    
                    host = text_inputs["Server Host"]
                    
                    status, result = play.post_json(host, "/admin-login", {"password": text_inputs["Admin Password"]})
                    
                    if status == 0:
                        error = result.get("error") or "host not found"
                        break
                    
                    if result["ok"]:
                        admin_panel_menu_view(ui,
                            host,
                            text_inputs["Admin Password"]
                        )
                        return
                    else:
                        error = "wrong password"
                        break
                
                elif key in ["DOWN", "ENTER", "TAB"]:
                    pointer += 1
                    pointer %= len(text_inputs) + 1
                    break
                elif key == "BACKSPACE" and pointer < len(text_inputs):
                    text_inputs[list(text_inputs.keys())[pointer]] = (
                        text_inputs[list(text_inputs.keys())[pointer]][:-1]
                    )
                    break
                elif (key.isalpha() or key.isdigit() or not key.isalnum()) and len(key) == 1 and pointer < len(text_inputs):
                    text_inputs[list(text_inputs.keys())[pointer]] += key
                    break

def admin_panel_register_requests_view(ui, host, password):
    pointer_x = 0
    pointer_y = 0

    requests: list[str]
    error = ""
    
    with play.cbreak_stdin():
        while True:
            ui.reset_text()
            
            ui.back_button()
            
            try:
                status, data = play.get_json(host, "/register-requests")
                if not data.get("ok"):
                    error = ui.api_error(status, data, "could not load register requests")
                    requests = []
                else:
                    requests = data.get("register-requests", [])
                    error = ""
            
            except Exception as exc:
                error = str(exc)
                requests = []
            
            ui.label("Admin Panel", 4, play.UI.Color.RED)
            ui.label("Register Requests", 5, play.UI.Color.RED)
            if error:
                ui.label(error, 6, play.UI.Color.RED)
            elif len(requests) == 0:
                ui.label("No pending requests", 6, play.UI.Color.GRAY)
            
            if len(requests) > 3 and pointer_y > 1:
                ui.label(". . .", 7)
            
            show = min(max(0, pointer_y - 1), len(requests) - min(3, len(requests)))
            
            ui.selector(
                pointer_x, (
                    0
                    if pointer_y == 0 else (
                        2
                        if pointer_y == len(requests) - 1
                        and len(requests) > 2 else
                        1
                    )
                ),
                requests[show:show+3], 8
            )
            
            if len(requests) > 3 and pointer_y < len(requests) - 2:
                ui.label(". . .", 23)
            
            ui.draw("↑/↓/←/→: Move • ENTER/SPACE: Select • R: Reload • Q: Quit")
            
            while True:
                key = play.read_key()
                if key in (None, "q", "Q"):
                    exit()
                elif key == "ESC":
                    return
                elif key in (None, "r", "R"):
                    break
                elif key == "UP" and len(requests) > 0:
                    pointer_y -= 1
                    pointer_y %= len(requests)
                    break
                elif key == "DOWN" and len(requests) > 0:
                    pointer_y += 1
                    pointer_y %= len(requests)
                    break
                elif key == "RIGHT":
                    pointer_x += 1
                    pointer_x %= 2
                    break
                elif key == "LEFT":
                    pointer_x -= 1
                    pointer_x %= 2
                    break
                elif key in ["ENTER", " "]:
                    if len(requests) == 0:
                        error = "no pending registration requests"
                        break
                    
                    status, data = play.post_json(
                        host, [
                            "/admin-reject-register-requests",
                            "/admin-approve-register-requests"
                        ][pointer_x],
                        {
                            "username": requests[pointer_y],
                            "password": password
                        }
                    )
                    if data.get("ok"):
                        error = ""
                    else:
                        error = ui.api_error(status, data, "could not update registration request")
                    break

def admin_panel_menu_view(ui, host, password):
    pointer = 0
    options = [
        "View Registration Requests",
        "More Options To Come...",
    ]
    disabled = {1}
    status_text = ""
    
    with play.cbreak_stdin():
        while True:
            ui.reset_text()
    
            try:
                status, data = play.get_json(host, "/register-requests")
                if not data.get("ok"):
                    status_text = ui.api_error(status, data, "could not load registration request count")
                    amount = 0
                else:
                    amount = len(data.get("register-requests", []))
                    status_text = ""
            
            except Exception as exc:
                status_text = str(exc)
                amount = 0
            
            ui.label("Admin Panel", 4, play.UI.Color.RED)
            
            ui.menu(pointer, [f"{options[0]} ({amount})", options[1]], play.UI.Color.RED, 7, 40, disabled=disabled)
            
            footer_lines = []
            if status_text:
                footer_lines.append(play.UI.Color.RED.value + status_text + play.UI.Color.RESET.value)
            footer_lines.append("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
            ui.draw("\n".join(footer_lines))
            
            while True:
                key = play.read_key()
                if key in (None, "q", "Q"):
                    exit()
                elif key in (None, "r", "R"):
                    break
                elif key == "UP":
                    pointer -= 1
                    pointer %= len(options)
                    break
                elif key == "DOWN":
                    pointer += 1
                    pointer %= len(options)
                    break
                elif key in ["ENTER", " "]:
                    if pointer in disabled:
                        status_text = "more options are disabled"
                        break
                    admin_panel_register_requests_view(ui, host, password)
                    break

def run():
    try:
        ui = play.UI()
        
        admin_panel_login_view(ui)
        
    
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    run()
