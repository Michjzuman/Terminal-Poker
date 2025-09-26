import random
import time

import tools

def intro():
    pos = [tools.COLORS["red"], tools.COLORS["blue"], tools.COLORS["purple"], tools.COLORS["yellow"]]

    def getText(prob, colors):
        text = f"""+-------------------------------------------------------+
|                                                       |
|                                                       |
| {tools.COLORS["red"]}   __  __   {tools.COLORS["blue"]}      __      {tools.COLORS["yellow"]}     /\      {tools.COLORS["purple"]}     /\     {tools.COLORS["reset"]}   |
| {tools.COLORS["red"]}  |  \/  |  {tools.COLORS["blue"]}    _(  )_    {tools.COLORS["yellow"]}    /  \     {tools.COLORS["purple"]}    /  \    {tools.COLORS["reset"]}   |
| {tools.COLORS["red"]}   \    /   {tools.COLORS["blue"]}   (__  __)   {tools.COLORS["yellow"]}    \  /     {tools.COLORS["purple"]}   (_  _)   {tools.COLORS["reset"]}   |
| {tools.COLORS["red"]}     \/     {tools.COLORS["blue"]}      ||      {tools.COLORS["yellow"]}     \/      {tools.COLORS["purple"]}     ||     {tools.COLORS["reset"]}   |
|                                                       |
|                                                       |
|                                                       |
|                {tools.COLORS["gray"]}Michjzuman's Terminal-{tools.COLORS["reset"]}                 |
| {colors[0]}      _____ {colors[1]}   ____   {colors[2]}  ___ ___ {colors[3]}   _______ {colors[4]} _____    {tools.COLORS["reset"]} |
| {colors[0]}     /  _  |{colors[1]} /  __  \ {colors[2]} /  //  / {colors[3]}  /  ____/{colors[4]} /  _  |   {tools.COLORS["reset"]} |
| {colors[0]}    /   __/ {colors[1]}/  / /  /{colors[2]} /     /  {colors[3]}  /  /__ {colors[4]}  /     /    {tools.COLORS["reset"]} |
| {colors[0]}   /  /    {colors[1]}/  /_/  /{colors[2]} /  /\  \ {colors[3]}  /  /___ {colors[4]} /  /| |     {tools.COLORS["reset"]} |
| {colors[0]}  /__/     {colors[1]}\______/{colors[2]} /__/  \__\{colors[3]} /______/ {colors[4]}/__/ |_|     {tools.COLORS["reset"]} |
|                                                       |
|                                                       |
+-------------------------------------------------------+"""
        
        text = list(text)
        for i in range(len(text)):
            if text[i] == " " and random.randint(0, prob) == 0:
                text[i] = random.choice("*@+$%:=<>")
        
        return ''.join(text)

    colors = [
        random.choice(pos),
        random.choice(pos),
        random.choice(pos),
        random.choice(pos),
        random.choice(pos)
    ]

    for i in range(25):
        if i % 5 == 0:
            colors = [
                random.choice(pos),
                random.choice(pos),
                random.choice(pos),
                random.choice(pos),
                random.choice(pos)
            ]
        text = getText(round(i**3), colors)
        tools.clear()
        print(text)
        time.sleep(0.1)

if __name__ == "__main__":
    intro()