"""Render an SVG to PNG at twice its size with the pre-installed Chromium (Playwright)."""
import sys
from playwright.sync_api import sync_playwright
src, dst = sys.argv[1], sys.argv[2]
svg = open(src, encoding='utf-8').read()
import re
w = int(re.search(r'width="(\d+)"', svg).group(1)); h = int(re.search(r'height="(\d+)"', svg).group(1))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
    pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
    pg.wait_for_timeout(300)
    pg.locator("svg").screenshot(path=dst)
    b.close()
print("png", dst)
