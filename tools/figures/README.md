# Figure scripts for the A2 report

Optional: these need Playwright with Chromium. The app and the tests do not.

```bash
python tools/figures/make_diagram.py diagrams/system_diagram_v3.svg
python tools/figures/svg2png.py diagrams/system_diagram_v3.svg diagrams/system_diagram_v3.png
python tools/figures/story_capture.py . frames        # starts app.py on port 8000 and drives it in Chromium
python tools/figures/compose_storyboards.py frames storyboard/a2
```

`story_capture.py` uses temporary hold and log files, so `data/holds.json` and `tool_log.jsonl` are not touched.
