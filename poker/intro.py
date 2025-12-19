# under construction

import random

def intro():
    pos = [tools.COLORS["red"], tools.COLORS["blue"], tools.COLORS["purple"], tools.COLORS["yellow"]]

    def getText(prob, COLORS):
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
| {COLORS[0]}      _____ {COLORS[1]}   ____   {COLORS[2]}  ___ ___ {COLORS[3]}   _______ {COLORS[4]} _____    {tools.COLORS["reset"]} |
| {COLORS[0]}     /  _  |{COLORS[1]} /  __  \ {COLORS[2]} /  //  / {COLORS[3]}  /  ____/{COLORS[4]} /  _  |   {tools.COLORS["reset"]} |
| {COLORS[0]}    /   __/ {COLORS[1]}/  / /  /{COLORS[2]} /     /  {COLORS[3]}  /  /__ {COLORS[4]}  /     /    {tools.COLORS["reset"]} |
| {COLORS[0]}   /  /    {COLORS[1]}/  /_/  /{COLORS[2]} /  /\  \ {COLORS[3]}  /  /___ {COLORS[4]} /  /| |     {tools.COLORS["reset"]} |
| {COLORS[0]}  /__/     {COLORS[1]}\______/{COLORS[2]} /__/  \__\{COLORS[3]} /______/ {COLORS[4]}/__/ |_|     {tools.COLORS["reset"]} |
|                                                       |
|                                                       |
+-------------------------------------------------------+"""
        
        text = list(text)
        for i in range(len(text)):
            if text[i] == " " and random.randint(0, prob) == 0:
                text[i] = random.choice("*@+$%:=<>")
        
        return ''.join(text)

    COLORS = [
        random.choice(pos),
        random.choice(pos),
        random.choice(pos),
        random.choice(pos),
        random.choice(pos)
    ]

    for i in range(25):
        if i % 5 == 0:
            COLORS = [
                random.choice(pos),
                random.choice(pos),
                random.choice(pos),
                random.choice(pos),
                random.choice(pos)
            ]
        text = getText(round(i**3), COLORS)
        tools.clear()
        print(text)
        time.sleep(0.1)
