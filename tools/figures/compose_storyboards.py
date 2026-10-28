"""Compose storyboard figures from the captured frames (real screenshots) and render them to PNG."""
import os
import sys

from playwright.sync_api import sync_playwright

FRAMES = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)

STATUS = ("Real screenshots of the v3 prototype, 28 Oct 2026. The language-model step is simulated; "
          "all data is made up; a hold is kept only in a local file.")

BOARDS = [
    {"file": "storyboard_1_clear_request_and_hold", "title": "Storyboard 1 · Alex asks for a pitch, checks a rule and holds it",
     "frames": [
         ("s1_f1.png", "Alex types: “Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up”",
          "Chips show what it understood (orange = assumed). Pitch 7, with its reasons."),
         ("s1_f2.png", "Alex asks: “When is quiet time?”",
          "Answer quoted from the guest information, with source, date and score. The booking is kept."),
         ("s1_f3.png", "Alex presses Hold this pitch",
          "Confirmation names the pitch, nights, party and what happens. Nothing has run."),
         ("s1_f4.png", "Alex presses Hold Pitch 7",
          "The tool runs. The report is built from its result: held for 48 hours, nothing paid."),
     ]},
    {"file": "storyboard_2_bella_ask_before_guessing", "title": "Storyboard 2 · Alex mentions Bella: ask before guessing, then correct an assumption",
     "frames": [
         ("s2_f1.png", "Alex types: “hi, two of us plus Bella in the campervan, need power, mid August”",
          "No pitch yet. Dates are vague and Bella could be a guest or a pet: two questions, quick replies."),
         ("s2_f2.png", "Alex replies: “14-16 Aug, Bella's our dog”",
          "Bella counted as a dog. Pitch 12 in the dog-friendly field. The van's length is assumed."),
         ("s2_f3.png", "Alex presses Hold this pitch",
          "The confirmation says the length was assumed. Alex can still cancel."),
         ("s2_f4.png", "Alex cancels, taps the orange chip and types “campervan 7.5m”",
          "The chip turns green (changed). Pitch 12 still fits a 7.5 m van."),
         ("s2_f5.png", "Alex holds Pitch 12 again and confirms",
          "Held for 14–16 Aug, reported from the tool's result."),
     ]},
    {"file": "storyboard_3_questions_and_limits", "title": "Storyboard 3 · Questions the guest information answers badly or not at all",
     "frames": [
         ("s3_f1.png", "A guest asks: “What is your cancellation policy?”",
          "The replaced 2026 edition ranks first. The page warns, answers from the 2027 edition and shows both."),
         ("s3_f2.png", "The guest asks: “Is there a swimming pool?”",
          "Nothing scores 0.25 or more, so it won't guess. No evidence shown; ask reception."),
         ("s3_f3.png", "The guest asks: “Can I cancel my booking?”",
          "An action it can't take: it says what it can do and hands over to reception."),
     ]},
]

CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #fff; font: 15px/1.4 Inter, 'Segoe UI', Helvetica, Arial, sans-serif; color: #1d2a22; }
.board { width: 1200px; padding: 26px 28px 30px; }
h1 { margin: 0 0 4px; font-size: 23px; font-weight: 700; }
.status { margin: 0 0 18px; color: #5d6b62; font-size: 14px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 22px; align-items: start; }
.frame { border: 1.5px solid #cfd8d1; border-radius: 12px; padding: 12px 12px 10px; background: #fafbfa; }
.head { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 9px; }
.num { flex: none; width: 28px; height: 28px; border-radius: 50%; background: #2f5d43; color: #fff;
       font-weight: 700; display: grid; place-items: center; font-size: 15px; }
.action { font-weight: 650; font-size: 15.5px; padding-top: 3px; }
.shot { width: 100%; display: block; border-radius: 10px; border: 1px solid #dde3de; }
.result { margin-top: 8px; color: #33413a; font-size: 14.5px; }
.result b { color: #2e7d4f; }
.span2 { grid-row: span 2; }
"""


def html(board):
    frames = []
    for i, (img, action, result) in enumerate(board["frames"], 1):
        extra = " span2" if board["file"].startswith("storyboard_3") and i == 1 else ""
        frames.append(f'<div class="frame{extra}"><div class="head"><div class="num">{i}</div>'
                      f'<div class="action">{action}</div></div>'
                      f'<img class="shot" src="{os.path.join(FRAMES, img)}">'
                      f'<div class="result"><b>System:</b> {result}</div></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="board"><h1>{board["title"]}</h1><p class="status">{STATUS}</p>'
            f'<div class="grid">{"".join(frames)}</div></div></body></html>')


with sync_playwright() as p:
    browser = p.chromium.launch()
    for board in BOARDS:
        path = os.path.join(OUT, board["file"] + ".html")
        open(path, "w", encoding="utf-8").write(html(board))
        page = browser.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=2)
        page.goto("file://" + path)
        page.wait_for_timeout(400)
        page.locator(".board").screenshot(path=os.path.join(OUT, board["file"] + ".png"))
        page.close()
        print("wrote", board["file"] + ".png")
    browser.close()
