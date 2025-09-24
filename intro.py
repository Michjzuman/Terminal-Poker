import random
import time

import tools

def play():
    pos = [tools.RED, tools.BLUE, tools.PURPLE, tools.YELLOW]

    def getText(prob, colors):
        text = f"""+--------------------------------------------------------+
|                                                        |
|                                                        |
|  {tools.RED}   __  __   {tools.BLUE}      __      {tools.YELLOW}     /\      {tools.PURPLE}     /\     {tools.RESET}   |
|  {tools.RED}  |  \/  |  {tools.BLUE}    _(  )_    {tools.YELLOW}    /  \     {tools.PURPLE}    /  \    {tools.RESET}   |
|  {tools.RED}   \    /   {tools.BLUE}   (__  __)   {tools.YELLOW}    \  /     {tools.PURPLE}   (_  _)   {tools.RESET}   |
|  {tools.RED}     \/     {tools.BLUE}      ||      {tools.YELLOW}     \/      {tools.PURPLE}     ||     {tools.RESET}   |
|                                                        |
|                                                        |
|                                                        |
|                 {tools.GRAY}Michjzuman's Terminal-{tools.RESET}                 |
|  {colors[0]}      _____ {colors[1]}   ____   {colors[2]}  ___ ___ {colors[3]}   _______ {colors[4]} _____    {tools.RESET} |
|  {colors[0]}     /  _  |{colors[1]} /  __  \ {colors[2]} /  //  / {colors[3]}  /  ____/{colors[4]} /  _  |   {tools.RESET} |
|  {colors[0]}    /   __/ {colors[1]}/  / /  /{colors[2]} /     /  {colors[3]}  /  /__ {colors[4]}  /     /    {tools.RESET} |
|  {colors[0]}   /  /    {colors[1]}/  /_/  /{colors[2]} /  /\  \ {colors[3]}  /  /___ {colors[4]} /  /| |     {tools.RESET} |
|  {colors[0]}  /__/     {colors[1]}\______/{colors[2]} /__/  \__\{colors[3]} /______/ {colors[4]}/__/ |_|     {tools.RESET} |
|                                                        |
|                                                        |
+--------------------------------------------------------+"""
        
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
    play()