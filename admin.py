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
    ui.note = "↑/↓: Move • ENTER: Confirm • ^C: Quit"
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
            
            ui.draw()
            
            
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
                    if not "http://" in host:
                        host = "http://" + host
                    
                    status, result = play.post_json(host, "/admin-login", {"password": text_inputs["Admin Password"]})
                    
                    if status == 0:
                        error = "host not found"
                        break
                    
                    if result["ok"]:
                        return text_inputs["Server Host"], text_inputs["Admin Password"]
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
    ui.note = "↑/↓/←/→: Move • ENTER/SPACE: Select • R: Reload • Q: Quit"
    pointer_x = 0
    pointer_y = 0

    requests: list[str]
    
    with play.cbreak_stdin():
        while True:
            ui.reset_text()
            
            ui.back_button()
            
            try:
                status, data = play.get_json(host, "/register-requests")
                requests = data["register-requests"]
            
            except TypeError or KeyError:
                requests = []
            
            ui.label("Admin Panel", 4, play.UI.Color.RED)
            ui.label("Register Requests", 5, play.UI.Color.RED)
            
            if len(requests) > 3 and pointer_y > 1:
                ui.label(". . .", 7)
            
            show = min(max(0, pointer_y - 1), len(requests) - 3)
            
            ui.selector(
                pointer_x, (0 if pointer_y == 0 else (2 if pointer_y == len(requests) - 1 else 1)),
                requests[show:show+3], 8
            )
            
            if len(requests) > 3 and pointer_y < len(requests) - 2:
                ui.label(". . .", 23)
            
            ui.draw()
            
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
                    
                    status, data = play.post_json(host, "/admin-approve-register-requests", {"username": requests[pointer_y], "password": password})

                    break

def admin_panel_menu_view(ui, host, password):
    ui.note = "↑/↓: Move • ENTER/SPACE: Select • Q: Quit"
    pointer = 0
    options = {
        "View Register Requests": admin_panel_register_requests_view,
        "More Options To Come...": None,
    }
    
    with play.cbreak_stdin():
        while True:
            ui.reset_text()
    
            try:
                status, data = play.get_json(host, "/register-requests")
                amount = len(data["register-requests"])
            
            except TypeError:
                amount = 0
            
            ui.label("Admin Panel", 4, play.UI.Color.RED)
            
            ui.menu(pointer, [f"{list(options.keys())[0]} ({amount})"], play.UI.Color.RED, 7, 40)
            ui.menu(pointer - 1, list(options.keys())[1:], play.UI.Color.RED, 10, 40)
            
            ui.draw()
            
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
                    list(options.values())[pointer](ui, host, password)
                    break

def run():
    try:
        ui = play.UI()
        
        host, password = "http://localhost:6767", "hello"
        #host, password = admin_panel_login_view(ui)
        
        admin_panel_register_requests_view(ui, host, password)
        
    
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    run()
