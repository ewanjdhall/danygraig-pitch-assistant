"""Draw the v3 system diagram for the A2 report as SVG (rendered to PNG separately)."""
import sys

W, H = 1800, 1100
out = []
FONT = "Inter, Segoe UI, Helvetica, Arial, sans-serif"
INK, MUTED = "#1d2a22", "#5d6b62"
STYLE = {
    "impl": dict(fill="#f1f8f3", stroke="#2e7d4f", dash=None),
    "sim": dict(fill="#fff5e6", stroke="#c26a00", dash="7 5"),
    "plan": dict(fill="#f5f6f5", stroke="#8a908c", dash="2 5"),
    "guest": dict(fill="#e9f1fb", stroke="#1d4f8f", dash=None),
    "box": dict(fill="#fbfcfb", stroke="#2e7d4f", dash=None),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=14, weight=400, anchor="start", fill=INK, italic=False):
    style = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
               f'fill="{fill}"{style}>{esc(s)}</text>')


def box(x, y, w, h, kind, title, lines=(), title_size=17, line_size=14.5, rx=10):
    s = STYLE[kind]
    dash = f' stroke-dasharray="{s["dash"]}"' if s["dash"] else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{s["fill"]}" '
               f'stroke="{s["stroke"]}" stroke-width="2.2"{dash}/>')
    text(x + 14, y + 24, title, title_size, 650, fill=INK if kind != "plan" else "#4b524e")
    for i, line in enumerate(lines):
        text(x + 14, y + 25 + 21 * (i + 1), line, line_size, 400, fill=INK if kind != "plan" else "#5d6b62")


def cylinder(x, y, w, h, kind, title, lines=()):
    s = STYLE[kind]
    e = 12
    out.append(f'<path d="M {x} {y + e} L {x} {y + h - e} A {w / 2} {e} 0 0 0 {x + w} {y + h - e} '
               f'L {x + w} {y + e}" fill="{s["fill"]}" stroke="{s["stroke"]}" stroke-width="2.2"/>')
    out.append(f'<ellipse cx="{x + w / 2}" cy="{y + e}" rx="{w / 2}" ry="{e}" fill="{s["fill"]}" '
               f'stroke="{s["stroke"]}" stroke-width="2.2"/>')
    text(x + w / 2, y + e + 28, title, 16.5, 650, "middle")
    for i, line in enumerate(lines):
        text(x + w / 2, y + e + 28 + 20 * (i + 1), line, 14.5, 400, "middle")


def pill(x, y, label, fill="#6b4fbb", w=None, ink="#fff"):
    w = w or (len(label) * 7.0 + 22)
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{fill}"/>')
    text(x + w / 2, y + 15.5, label, 12, 650, "middle", ink)
    return w


def arrow(points, kind="impl", both=False, width=2.0):
    color = {"impl": "#33413a", "sim": "#c26a00", "plan": "#8a908c", "bound": "#6b4fbb"}[kind]
    dash = {"impl": "", "sim": ' stroke-dasharray="7 5"', "plan": ' stroke-dasharray="3 5"', "bound": ""}[kind]
    d = "M " + " L ".join(f"{px} {py}" for px, py in points)
    start = f' marker-start="url(#h_{kind})"' if both else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash} '
               f'marker-end="url(#h_{kind})"{start}/>')


def label(x, y, lines, size=13, anchor="start", fill="#33413a", italic=True):
    for i, s in enumerate(lines):
        text(x, y + i * (size + 3), s, size, 400, anchor, fill, italic)


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">')
out.append('<rect width="100%" height="100%" fill="#ffffff"/>')
out.append("<defs>" + "".join(
    f'<marker id="h_{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
    f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>'
    for k, c in (("impl", "#33413a"), ("sim", "#c26a00"), ("plan", "#8a908c"), ("bound", "#6b4fbb"))) + "</defs>")

text(40, 44, "Danygraig pitch assistant: system diagram (v3, 28 October 2026)", 26, 700)
text(40, 72, "Components, the information and control flows between them, and what is implemented, simulated "
             "or planned. All pitch, booking and guest-information data is made up.", 14.5, 400, fill=MUTED)

# legend
lx, ly = 1180, 96
for i, (kind, name) in enumerate((("impl", "Implemented"), ("sim", "Simulated"), ("plan", "Planned"),
                                  ("guest", "Person"))):
    s = STYLE[kind]
    dash = f' stroke-dasharray="{s["dash"]}"' if s["dash"] else ""
    x = lx + i * 150
    out.append(f'<rect x="{x}" y="{ly}" width="34" height="20" rx="5" fill="{s["fill"]}" stroke="{s["stroke"]}" '
               f'stroke-width="2.2"{dash}/>')
    text(x + 42, ly + 15, name, 14)

# ---------------------------------------------------------------- left column: the guest and the page
box(40, 126, 300, 80, "guest", "Guest", ["types a trip or a question; taps chips;", "presses Hold, Confirm or Cancel"])
box(40, 240, 300, 238, "impl", "Chat page (index.html)", [
    "chips: stated · assumed · ? unclear",
    "clarifying questions + quick replies",
    "pitch card with its reasons",
    "answer + where it comes from:",
    "  passage, source, date, score",
    "stale warning or “ask reception”",
    "hold confirmation with arguments",
    "Lab 4 checks (images, invalid hold)",
    "“What the system did” (trace)"])
arrow([(190, 206), (190, 240)], both=True)

# ---------------------------------------------------------------- middle: app.py
out.append('<rect x="420" y="210" width="660" height="660" rx="14" fill="#fbfcfb" stroke="#2e7d4f" '
           'stroke-width="1.6"/>')
text(440, 236, "app.py · turn(message, state, action)  (Python standard library, localhost:8000)", 14.5, 650,
     fill="#2e5d43")

X, BW = 480, 575
box(X, 252, BW, 60, "impl", "Context assembly + log_context(parts)",
    ["instructions + requirements so far + the message"])
pill(X + BW - 196, 241, "planned: today's date", fill="#e6e8e6", w=184, ink="#4b524e")
box(X, 332, BW, 78, "sim", "Extraction step · model.call_json(parts, schema v3)",
    ["each field: value + source + the guest's words,", "or the message is a question about the park"])
box(X, 422, BW, 60, "impl", "validate(): ask before guessing",
    ["dates · party · vehicle · names like “Bella” → at most 2 questions"])
box(X, 502, BW, 60, "impl", "Availability lookup and ranking",
    ["fits · free · not held by another guest · reasons for each pitch"])
box(X, 582, BW, 60, "impl", "Answer path · answer_turn()",
    ["top 3 passages · score ≥ 0.25 · prefer the current edition"])
box(X, 662, BW, 60, "sim", "Answer step · quotes the chosen passage",
    ["gets instructions + quoted passages + question; no booking details"])
box(X, 778, BW, 74, "impl", "Hold proposal, built by the app (never by the model)",
    ["from the chips and the pitch the guest chose; confirmation shows the", "arguments and marks assumed values; report built from the tool's result"])

# flows inside app.py
arrow([(767, 312), (767, 332)])
arrow([(700, 410), (700, 422)])
arrow([(700, 482), (700, 502)])
label(708, 497, ["complete"], 11.5)
arrow([(480, 388), (456, 388), (456, 612), (480, 612)])
out.append('<text x="441" y="500" font-size="11.5" font-style="italic" fill="#33413a" text-anchor="middle" '
           'transform="rotate(-90 441 500)">a question → answer path</text>')
arrow([(767, 642), (767, 662)])

# autonomy boundary
out.append('<path d="M 432 752 L 480 752" stroke="#6b4fbb" stroke-width="2.4" stroke-dasharray="9 6"/>')
out.append('<path d="M 1010 752 L 1068 752" stroke="#6b4fbb" stroke-width="2.4" stroke-dasharray="9 6"/>')
pill(X, 741, "autonomy boundary", w=150)
text(X + 162, 757, "above: suggests · below: acts only after the guest confirms", 12.5, 600, fill="#6b4fbb")

# request / response between page and app
arrow([(340, 282), (480, 282)])
label(347, 262, ["request"], 11.5)
label(347, 300, ["message,", "state, action"], 11.5)
arrow([(420, 455), (340, 455)])
label(347, 446, ["response"], 11.5)
label(347, 472, ["render(data)"], 11.5)

# ---------------------------------------------------------------- right column: data, tools, planned
RX = 1160
box(RX, 330, 360, 80, "plan", "A real LLM (planned)",
    ["same parts and schema; its key from an", "environment variable, never in the code"])
arrow([(RX, 367), (1055, 367)], kind="plan")

cylinder(RX, 478, 400, 110, "impl", "data/ (made-up)",
         ["pitches.json (14) · bookings.json (7)", "holds.json: active holds"])
arrow([(RX, 532), (1055, 532)])
label(1068, 524, ["reads"], 11.5)

cylinder(RX, 604, 330, 112, "impl", "corpus/: guest information",
         ["7 made-up documents, 1 superseded", "retrieve.py: word overlap, top 3"])
pill(RX + 50, 691, "planned: match meaning, not words", fill="#e6e8e6", w=230, ink="#4b524e")
arrow([(1055, 625), (RX, 625)], both=True)
label(1066, 614, ["question"], 11.5)
label(1066, 642, ["passages +", "source, date,", "score"], 11.5)

box(RX, 778, 360, 74, "impl", "hold_tool.py · hold_pitch",
    ["checks: shape · permission · precondition", "confirmation · idempotency · logged"])
arrow([(1055, 800), (RX, 800)])
label(1064, 792, ["after Confirm"], 11.5)
arrow([(RX, 836), (1055, 836)])
label(1066, 852, ["result"], 11.5)
arrow([(1510, 778), (1510, 580)])
label(1518, 690, ["writes", "a hold"], 11.5)
box(RX, 890, 360, 46, "impl", "tool_log.jsonl: one line per call", [], title_size=14.5)
arrow([(1340, 852), (1340, 890)])

box(1580, 778, 200, 74, "plan", "Booking, payment,", ["email (planned)"])
arrow([(1520, 815), (1580, 815)], kind="plan")

# ---------------------------------------------------------------- bottom left: image checks
box(40, 900, 300, 76, "sim", "vlm.py: the lab's mock", ["2 sample images: claim + confidence,", "or refusal + reason"])
arrow([(500, 870), (500, 933), (340, 933)])
label(350, 924, ["image check"], 11.5)
box(40, 1004, 300, 82, "plan", "Photo of a van's plate (planned)", ["read its length, shown as an", "assumed value with its confidence"])
arrow([(190, 1004), (190, 976)], kind="plan")

text(420, 1040, "Passages are quoted as data, not instructions · only the guest's Confirm reaches the hold tool",
     13, 600, fill="#6b4fbb")

out.append("</svg>")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
print("wrote", sys.argv[1])
