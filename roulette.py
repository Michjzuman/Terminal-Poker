from main import clear, RED, BLUE, RESET, GRAY

def roulette():
    clear()
    
    options = [
        {"text": " 0 ", "color": "white"},
        {"text": " 00 ", "color": "white"},
        {"text": " 1 ", "color": "black"},
        {"text": " 2 ", "color": "red"},
        {"text": " 3 ", "color": "black"},
        {"text": " 4 ", "color": "black"},
        {"text": " 5 ", "color": "red"},
        {"text": " 6 ", "color": "black"},
        {"text": " 7 ", "color": "red"},
        {"text": " 8 ", "color": "black"},
        {"text": " 9 ", "color": "red"},
        {"text": " 10 ", "color": "black"},
        {"text": " 11 ", "color": "red"},
        {"text": " 12 ", "color": "black"},
        {"text": " 13 ", "color": "red"},
        {"text": " 14 ", "color": "black"},
        {"text": " 15 ", "color": "red"},
        {"text": " 16 ", "color": "black"},
        {"text": " 17 ", "color": "red"},
        {"text": " 18 ", "color": "black"},
        {"text": " 19 ", "color": "red"},
        {"text": " 20 ", "color": "black"},
        {"text": " 21 ", "color": "red"},
        {"text": " 22 ", "color": "black"},
        {"text": " 23 ", "color": "red"},
        {"text": " 24 ", "color": "black"},
        {"text": " 25 ", "color": "red"},
        {"text": " 26 ", "color": "black"},
        {"text": " 27 ", "color": "red"},
        {"text": " 28 ", "color": "black"},
        {"text": " 29 ", "color": "red"},
        {"text": " 30 ", "color": "black"},
        {"text": " 31 ", "color": "red"},
        {"text": " 32 ", "color": "black"},
        {"text": " 33 ", "color": "red"},
        {"text": " 34 ", "color": "black"},
        {"text": " 35 ", "color": "red"},
        {"text": " 36 ", "color": "black"},
        {"text": "EVEN", "color": "white"},
        {"text": "ODD", "color": "white"},
        {"text": "BLACK", "color": "black"},
        {"text": "RED", "color": "red"},
        {"text": "1to18", "color": "white"},
        {"text": "1nd12", "color": "white"},
        {"text": "2nd12", "color": "white"},
        {"text": "3nd12", "color": "white"},
        {"text": "2to1", "color": "white"},
        {"text": "19to36", "color": "white"},
    ]

    text = f"""                +-------+------+
                |   0   |  00  |
+-------+-------+----+----+----+
|       |       |  1 |  2 |  3 |
| 1to18 |       +----+----+----|
|       | 1nd12 |  4 |  5 |  6 |
+-------+       +----+----+----|
|       |       |  7 |  8 |  9 |
| EVEN  |       +----+----+----|
|       |       | 10 | 11 | 12 |
+-------+-------+----+----+----+
|       |       | 13 | 14 | 15 |
|  RED  |       +----+----+----|
|       | 2nd12 | 16 | 17 | 18 |
+-------+       +----+----+----|
|       |       | 19 | 20 | 21 |
| BLACK |       +----+----+----|
|       |       | 22 | 23 | 24 |
+-------+-------+----+----+----+
|       |       | 25 | 26 | 27 |
|  ODD  |       +----+----+----|
|       | 2nd12 | 28 | 29 | 30 |
+-------+       +----+----+----|
|       |       | 31 | 32 | 33 |
| 19to36|       +----+----+----|
|       |       | 34 | 35 | 36 |
+-------+-------+----+----+----+
                |2to1|2to1|2to1|
                +----+----+----+"""
    
    for option in options:
        text = text.replace(option["text"], option["color"] + option["text"] + "gray")
    for color in [["white", RESET], ["gray", GRAY], ["red", RED], ["black", BLUE]]:
        text = text.replace(color[0], color[1])

    text = text.split("\n")
    for i in range(len(text)):
        text[i] = GRAY + text[i]
    text = "\n".join(text) + RESET

    print(text)
