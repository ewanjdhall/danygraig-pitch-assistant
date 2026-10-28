"""Capture storyboard frames from the running prototype (real screenshots, device scale 2)."""
import os
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import sync_playwright

proj, outdir = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(outdir, exist_ok=True)
tmp = tempfile.mkdtemp(prefix="story_")
env = dict(os.environ, DANYGRAIG_HOLDS=os.path.join(tmp, "holds.json"),
           DANYGRAIG_TOOL_LOG=os.path.join(tmp, "tool_log.jsonl"))
srv = subprocess.Popen([sys.executable, "-u", "app.py"], cwd=proj, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)


def bots(pg):
    return pg.evaluate("document.querySelectorAll('.msg.bot').length")


def wait_new(pg, n):
    pg.wait_for_function(f"document.querySelectorAll('.msg.bot').length > {n}")
    time.sleep(0.4)


def say(pg, text):
    n = bots(pg)
    pg.fill("#message", text)
    pg.click("button[type=submit]")
    wait_new(pg, n)


def click(pg, selector):
    n = bots(pg)
    pg.click(selector)
    wait_new(pg, n)


def shot(pg, name, hide_trace=True):
    bubble = pg.locator(".msg.bot").last
    if hide_trace:  # the "What the system did" line adds nothing to a storyboard frame
        pg.evaluate("document.querySelectorAll('details.trace').forEach(d => d.style.display = 'none')")
    bubble.screenshot(path=os.path.join(outdir, name))
    print("frame", name)


try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Storyboard 1: Alex, a clear request, a question, then a hold
        pg = browser.new_page(viewport={"width": 660, "height": 1400}, device_scale_factor=2)
        pg.goto("http://localhost:8000")
        say(pg, "Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up")
        shot(pg, "s1_f1.png")
        say(pg, "When is quiet time?")
        shot(pg, "s1_f2.png")
        pg.click(".msg.bot >> nth=1 >> text=Hold this pitch")
        pg.wait_for_function("document.querySelectorAll('.msg.bot').length > 3")
        time.sleep(0.4)
        shot(pg, "s1_f3.png")
        click(pg, ".msg.bot >> nth=-1 >> .confirm button.primary")
        shot(pg, "s1_f4.png")
        pg.close()

        # Storyboard 2: Alex with Bella: questions, an assumed length caught at the confirmation, a correction
        pg = browser.new_page(viewport={"width": 660, "height": 1400}, device_scale_factor=2)
        pg.goto("http://localhost:8000")
        say(pg, "hi, two of us plus Bella in the campervan, need power, mid August")
        shot(pg, "s2_f1.png")
        say(pg, "14-16 Aug, Bella's our dog")
        shot(pg, "s2_f2.png")
        click(pg, ".msg.bot >> nth=-1 >> text=Hold this pitch")
        shot(pg, "s2_f3.png")
        click(pg, ".msg.bot >> nth=-1 >> .confirm button.secondary")
        # tap the orange (assumed) vehicle chip in the last recommendation and type the real length
        chip = pg.locator(".msg.bot .chip.assumed[data-field=vehicle]").last
        chip.click()
        n = bots(pg)
        pg.locator("input.chip-edit").fill("campervan 7.5m")
        pg.locator("input.chip-edit").press("Enter")
        wait_new(pg, n)
        shot(pg, "s2_f4.png")
        click(pg, ".msg.bot >> nth=-1 >> text=Hold this pitch")
        click(pg, ".msg.bot >> nth=-1 >> .confirm button.primary")
        shot(pg, "s2_f5.png")
        pg.close()

        # Storyboard 3: questions the guest information answers badly or not at all
        pg = browser.new_page(viewport={"width": 660, "height": 1400}, device_scale_factor=2)
        pg.goto("http://localhost:8000")
        say(pg, "What is your cancellation policy?")
        shot(pg, "s3_f1.png")
        say(pg, "Is there a swimming pool?")
        shot(pg, "s3_f2.png")
        say(pg, "Can I cancel my booking?")
        shot(pg, "s3_f3.png")
        pg.close()
        browser.close()
finally:
    srv.terminate()
