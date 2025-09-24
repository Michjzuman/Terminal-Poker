const ALL_NUMS = "234567891JQKA";
const ALL_KINDS = [
    {"letter": "H", "digit": "♥", "color": "red"},
    {"letter": "C", "digit": "♣", "color": "purple"},
    {"letter": "D", "digit": "♦", "color": "orange"},
    {"letter": "S", "digit": "♠", "color": "blue"}
];

const intro = {
    "prob": 100,
    "here": true
}

async function getData() {
    const response = await fetch("./data.json");
    if (!response.ok) return;
    const data = await response.json();

    const publicCards = [
        card(true, "H", "J"),
        card(true, "D", "7"),
        card(true, "S", "A"),
        card(true, "C", "K"),
        card(true, "H", "Q")
    ]

    function card(shown=true, kind="H", num="7") {
        if (shown) {
            const color = ALL_KINDS.find(k => k.letter === kind).color;
            const digit = ALL_KINDS.find(k => k.letter === kind).digit;
            let text = "";
            data.ascii.cards[num].forEach(line => {
                if (line[0] != "+") {
                    line = `${line.slice(0, 1)}<${color}>${line.slice(1, 8)}</${color}>${line.slice(8)}`;
                }
                line = line.replaceAll("X", digit) + "<br>";
                text += line;
            });
            return `
                <div class="card" id="${kind}${num}">
                    <p class="ascii">${text}</p>
                </div>
            `;
        } else {
            let text = "";
            data.ascii.cards["Back"].forEach(line => {
                text += line + "<br>";
            });
            return `
                <div class="card" id="Back">
                    <p class="ascii gray">${text}</p>
                </div>
            `;
        }
    }

    function drawTitle() {
        const colors = [
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color
        ];
        let res = [];
        data.ascii.title.forEach(line => {
            let r = ""
            line.split("X").forEach((letter, i) => {
                r += `<${colors[i]}>${letter}</${colors[i]}>`;
            });
            res.push(r);
        });
        return res.join("<br>");
    }

    function drawIntro() {
        const prob = intro.prob;
        const colors = ["red", "purple", "orange", "blue"];
        const randomColors = [
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color,
            ALL_KINDS[Math.round(Math.random() * 3)].color
        ];
        let res = [];
        data.ascii.intro.forEach((line, y) => {
            let r = ""
            if (y > 2 && y < 7) {
                line.split("X").forEach((part, i) => {
                    r += `<${colors[i - 1]}>${part.slice(0, part.length - 1)}</${colors[i - 1]}>${part[part.length - 1]}`;
                });
            } else if (y == 10) {
                r = `${line[0]}<gray>${line.slice(1, 57)}</gray>${line[57]}`;
            } else if (y > 10 && y < 16) {
                line.split("X").forEach((part, i) => {
                    r += `<${randomColors[i - 1]}>${part.slice(0, part.length - 1)}</${randomColors[i - 1]}>${part[part.length - 1]}`;
                });
            } else {
                r = line;
            }
            res.push(r);
        });
        let result = ""
        res.join("<br>").split("").forEach(letter => {
            if (letter == " " && (Math.random() < (prob / 100))) {
                const pos = "#*+!@†&%?.:-michjzuman♥♣♦♠";
                result += pos[Math.round(Math.random() * (pos.length - 1))];
            } else {
                result += letter;
            }
        });
        intro.prob *= 0.7;
        if (intro.prob <= 0.01) {
            intro.here = false;
            clearInterval(introInterval);
            document.querySelector("body").classList.remove("intro");
        }
        return result;
    }

    document.querySelector("div.public.cards").innerHTML = publicCards.join("");

    document.querySelector("p.title").innerHTML = drawTitle();
    setInterval(() => {
        document.querySelector("p.title").innerHTML = drawTitle();
    }, 1000);
    
    document.querySelector("p.intro").innerHTML = drawIntro();
    const introInterval = setInterval(() => {
        document.querySelector("p.intro").innerHTML = drawIntro();
    }, 100);
}


function main() {
    getData();
}

main();