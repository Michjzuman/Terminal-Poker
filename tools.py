import os
import platform
import shutil
import json

RED = "\033[31m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
YELLOW = "\033[38;5;214m"
GRAY = "\033[90m"
GREEN = "\033[32m"
RESET = "\033[0m"

ALL_KINDS = "CHSD"
ALL_NUMS = "234567891JQKA"

PATH = os.path.dirname(os.path.abspath(__file__))

def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def read_file(f):
    if os.stat(f).st_size == 0:
        return {}
    with open(f, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def write_file(f, con):
    with open(f, "w") as file:
        file.write(json.dumps(con, indent=4))

def terminal_width():
    return shutil.get_terminal_size(fallback=(80, 24)).columns