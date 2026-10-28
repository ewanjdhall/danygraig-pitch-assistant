"""Replay the Lab 4 checks through app.turn() and write what happened.

Run from the project folder:  python tests/run_lab4.py
Uses temporary hold and log files, so data/holds.json and tool_log.jsonl (the record of the browser
checks) are not touched. Results go to tests/results/lab4_*.md and tests/results/LAB4_SUMMARY.md.
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp(prefix="lab4_tests_")
os.environ["DANYGRAIG_HOLDS"] = os.path.join(TMP, "holds.json")
os.environ["DANYGRAIG_TOOL_LOG"] = os.path.join(TMP, "tool_log.jsonl")
sys.path.insert(0, ROOT)

import app  # noqa: E402
import hold_tool  # noqa: E402

RESULTS = os.path.join(ROOT, "tests", "results")
TEST_A = "Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up"
TEST_B = ["hi, two of us plus Bella in the campervan, need power, mid August", "14-16 Aug, Bella's our dog"]


def quiet(fn, *args, **kwargs):
    """Run a turn, keeping its printed CONTEXT lines so they can be written to the result file."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        data = fn(*args, **kwargs)
    return data, [line for line in buffer.getvalue().splitlines() if line.startswith("CONTEXT:")]


def reset_tool_files():
    for name in ("holds.json", "tool_log.jsonl"):
        path = os.path.join(TMP, name)
        if os.path.exists(path):
            os.remove(path)


def log_lines():
    path = os.path.join(TMP, "tool_log.jsonl")
    return open(path, encoding="utf-8").read().splitlines() if os.path.exists(path) else []


def holds_now():
    return [{k: h[k] for k in ("id", "pitch", "check_in", "check_out", "session")} for h in hold_tool._load_holds()]


def describe_answer(data):
    lines = [f"> {data['reply']}"]
    if data.get("answer"):
        lines.append(f"> “{data['answer']['text']}”")
    if data.get("stale_warning"):
        lines.append(f"\n**Warning shown:** {data['stale_warning']}")
    if data.get("declined"):
        lines.append(f"\n**Declined:** best score {data['declined']['best_score']:.2f}, threshold "
                     f"{data['declined']['threshold']:.2f}; no evidence shown")
    if data.get("evidence"):
        lines += ["", "| shown as | source | section | updated | score | passage |", "|---|---|---|---|---|---|"]
        for h in data["evidence"]:
            role = "used for the answer" if h.get("used") else ("superseded" if h["superseded"] else "also found")
            lines.append(f"| {role} | {h['source']} | {h['section']} | {h['date']} | {h['score']:.2f} | "
                         f"{h['text'][:90]}{'…' if len(h['text']) > 90 else ''} |")
    return lines


def question_case(case, corpus=None):
    original = app.CORPUS_DIR
    if corpus:
        app.CORPUS_DIR = os.path.join(ROOT, corpus)
    try:
        data, context = quiet(app.turn, case["question"], version="v3", session="tests")
    finally:
        app.CORPUS_DIR = original
    retrieval = data["trace"].get("retrieval", [])
    lines = [f"# {case['title']}", "", f"Question: “{case['question']}”" + (f" (corpus: `{corpus}`)" if corpus else ""),
             "", "**Retrieval (top three, as ranked)**", ""]
    lines += [f"- {r['score']:.2f} `{r['file']}` {r['section']}, updated {r['date']}"
              f"{' [SUPERSEDED]' if r['superseded'] else ''}" for r in retrieval] or ["- nothing"]
    lines += ["", "**Context sent to the answer step**", "", "```text"] + context[-3:] + ["```", "",
              "**What the page showed**", ""] + describe_answer(data)
    if data.get("answer"):
        outcome = f"answered from {data['answer']['section']} ({data['answer']['date']}, score {data['answer']['score']:.2f})"
        if data.get("stale_warning"):
            outcome += ", stale warning shown"
    elif data.get("declined"):
        outcome = f"declined (best score {data['declined']['best_score']:.2f})"
    else:
        outcome = "no answer: " + data["reply"][:60]
    return lines, outcome


def tool_case(case):
    reset_tool_files()
    lines, notes = [f"# {case['title']}", ""], []
    states = {}

    def step(label, session, **kwargs):
        data, _ = quiet(app.turn, kwargs.pop("message", ""), states.get(session), version="v3",
                        session=session, **kwargs)
        states[session] = data.get("state", states.get(session))
        shown = data["reply"]
        if data.get("hold") and data["hold"].get("question"):
            shown += " | " + data["hold"]["question"] + " " + data["hold"]["consequence"]
        if data.get("hold") and data["hold"].get("result"):
            shown += " | tool result: " + json.dumps(data["hold"]["result"])
        if data.get("recommendation"):
            shown += f" | recommends {data['recommendation']['name']}"
        if data.get("near_misses"):
            shown += " | closest: " + "; ".join(f"{n['pitch']} ({n['why_not']})" for n in data["near_misses"])
        lines.append(f"- **{label}** ({session}): {shown}")
        return data

    for item in case["steps"]:
        kind = item["do"]
        session = item.get("session", "guest-1")
        if kind == "say":
            step(f"says “{item['message']}”", session, message=item["message"])
        elif kind == "propose":
            data = step(f"presses Hold this pitch on Pitch {item['pitch']}", session,
                        action={"type": "propose_hold", "pitch": item["pitch"]})
            if data.get("hold") and data["hold"].get("proposal"):
                states[(session, "proposal")] = data["hold"]["proposal"]
        elif kind == "propose_raw":
            step("sends a hand-written hold request: " + json.dumps(item["call"]["arguments"]), session,
                 action={"type": "propose_hold_raw", "call": item["call"]})
        elif kind in ("confirm", "cancel"):
            step("presses " + ("Hold Pitch (confirm)" if kind == "confirm" else "Cancel"), session,
                 action={"type": f"{kind}_hold", "proposal": states.get((session, "proposal"))})
    lines += ["", "**tool_log.jsonl after the case**", "", "```json"] + log_lines() + ["```", "",
              "**Holds in the file after the case**", "", "```json", json.dumps(holds_now(), indent=1), "```"]
    log = [json.loads(line) for line in log_lines()]
    outcome = "; ".join(f"{e['result']['status']}" + (f" ({e['result'].get('check')})" if e['result'].get('check') else "")
                        for e in log) or "nothing logged"
    outcome += f"; holds now: {len(holds_now())}"
    return lines, outcome


def image_case(case):
    data, _ = quiet(app.turn, "", None, version="v3", session="tests",
                    action={"type": "image_check", "image": case["image"]})
    image = data["image"]
    lines = [f"# {case['title']}", "", f"Image `{image['file']}`, question “{image['question']}”", "",
             f"> {data['reply']}", "", "```json", json.dumps({k: v for k, v in image.items()
                                                                 if k not in ("file", "question")}, indent=1), "```"]
    outcome = (f"refused: {image['reason']}" if image.get("refused")
               else f"{image['claim']} (confidence {image['confidence']:.2f})")
    return lines, outcome


def regression():
    """Every Lab 3 case should end the same way on v3 as on v2."""
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    import run_tests
    with open(os.path.join(ROOT, "tests", "cases.json"), encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    rows = []
    for case in cases:
        with redirect_stdout(io.StringIO()):
            v2 = run_tests.run_case(case, "v2")
            reset_tool_files()
            v3 = run_tests.run_case(case, "v3")
        same = [run_tests.outcome(v2[:i]) for i in range(1, len(v2) + 1)] == \
               [run_tests.outcome(v3[:i]) for i in range(1, len(v3) + 1)]
        rows.append((case["title"], run_tests.outcome(v3), "same as v2" if same else "DIFFERENT from v2"))
    return rows


def main():
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(ROOT, "tests", "lab4_cases.json"), encoding="utf-8") as f:
        spec = json.load(f)
    summary = ["# Lab 4 test results", "",
               "Replayed through `app.turn()` on v3 by `tests/run_lab4.py`, with temporary hold and log files. "
               "The browser checks are recorded separately in `02_TEST_RECORD.md`, `tool_log.jsonl` and `screenshots/`.", ""]
    summary += ["## Questions answered from the guest information", "", "| Case | Question | Outcome |", "|---|---|---|"]
    for case in spec["questions"]:
        lines, outcome = question_case(case, case.get("corpus"))
        open(os.path.join(RESULTS, f"lab4_{case['id']}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        summary.append(f"| {case['title']} | “{case['question']}” | {outcome} |")
        print(f"{case['id']:<28} {outcome}")
    summary += ["", "## The hold_pitch tool", "", "| Case | Outcome (log entries in order; holds in the file) |", "|---|---|"]
    for case in spec["tools"]:
        lines, outcome = tool_case(case)
        open(os.path.join(RESULTS, f"lab4_{case['id']}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        summary.append(f"| {case['title']} | {outcome} |")
        print(f"{case['id']:<28} {outcome}")
    summary += ["", "## Image checks (the lab's mock and sample images)", "", "| Case | Outcome |", "|---|---|"]
    for case in spec["images"]:
        lines, outcome = image_case(case)
        open(os.path.join(RESULTS, f"lab4_{case['id']}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        summary.append(f"| {case['title']} | {outcome} |")
        print(f"{case['id']:<28} {outcome}")
    summary += ["", "## Regression: the Lab 3 cases on v3", "", "| Lab 3 case | v3 after the last turn | Compared with v2 |",
                "|---|---|---|"]
    for title, outcome, same in regression():
        summary.append(f"| {title} | {outcome} | {same} |")
        print(f"{'regression':<28} {same}: {title[:50]}")
    with open(os.path.join(RESULTS, "LAB4_SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")


if __name__ == "__main__":
    main()
