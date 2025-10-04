import os
import platform
import shutil
import json
import random
import keyboard

COLORS = {
    "red": "\033[31m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "yellow": "\033[38;5;214m",
    "gray": "\033[90m",
    "green": "\033[32m",
    "reset": "\033[0m"
}

listen_keys = []

ALL_KINDS = "CHSD"
ALL_NUMS = "234567891JQKA"

PATH = os.path.dirname(os.path.abspath(__file__))

def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def terminal_width():
    return shutil.get_terminal_size(fallback=(80, 24)).columns

def colored(text):
    res = ""
    for letter in text:
        res += random.choice([
            COLORS["red"],
            COLORS["purple"],
            COLORS["yellow"],
            COLORS["blue"],
            COLORS["gray"]
        ])
        res += letter
        res += COLORS["reset"]
    return res

