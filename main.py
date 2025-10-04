#!/usr/bin/env python3

# Michjzuman's Terminal Poker

from datetime import datetime, timedelta
import time

import tools
import ascii
import find_hands

user = {
    "name": "Michjzuman",
    "money": 5,
    "dept": 5
}

def start_menu():
    tools.clear()
    print(ascii.menu(
        {
            "title": "Welcome to Michjzuman's Terminal Poker",
            "options": [
                {
                    "key": "l",
                    "action": "Login",
                    "color": "blue"
                },
                {
                    "key": "r",
                    "action": "Register",
                    "color": "purple"
                }
            ]
        }
    ))

def home_menu():
    tools.clear()
    print(ascii.menu(
        {
            "title": "Home:",
            "options": [
                {
                    "key": "p",
                    "action": "Play Poker",
                    "color": "yellow"
                },
                {
                    "key": "b",
                    "action": "Bank",
                    "color": "green"
                }
            ]
        }
    ))

def main(intro=True):
    if intro:
        ascii.animations.intro()
    
    start_menu()

if __name__ == "__main__":
    main(False)