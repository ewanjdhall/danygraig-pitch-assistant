"""Replay the test conversations through app.turn() and write what happened.

Run from the project folder:  python tests/run_tests.py
Each case runs on v1 (the original path) and v2 (after the Phase 4 changes).
Results go to tests/results/ (one Markdown file per case and version, plus SUMMARY.md).
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import app  # noqa: E402

RESULTS = os.path.join(ROOT, "tests", "results")


def chips_text(chips):
    marks = {"assumed": " (assumed)", "edited": " (changed)", "vague": " (vague)",
             "missing": " (missing)", "unclear": " (unclear)"}
    return " ".join(f"`{chip['label']}{marks.get(chip.get('source'), '')}`" for chip in chips) or "(none)"


def card_text(card):
    return f"**{card['title']}**: " + "; ".join(card["reasons"]) + f". {card['price']}"


def describe(step, data, number):
    lines = []
    if "message" in step:
        lines += [f"### Turn {number}: the guest types", "", f"> {step['message']}", ""]
        if step.get("why"):
            lines += [f"*Why: {step['why']}.*", ""]
    else:
        changes = ", ".join(f"{field} → {value}" for field, value in step["edits"].items())
        lines += [f"### Turn {number}: the guest edits chips ({changes})", ""]
        if step.get("why"):
            lines += [f"*Why: {step['why']}.*", ""]
    trace = data.get("trace", {})
    lines += ["**What the system received**", ""]
    for i, part in enumerate(trace.get("parts", []), 1):
        content = part["content"]
        if len(content) > 160:
            content = content[:157] + "..."
        lines.append(f"{i}. `{part['role']}`: {content}")
    if "edits" in step:
        lines.append(f"- Chip edits: `{json.dumps(step['edits'])}` (applied in app.py; no model call)")
    lines += ["", "**What it did**", ""]
    if "data_error" in trace:
        lines.append(f"- Loading the pitch data failed: `{trace['data_error']}`. No model call and no lookup.")
    if "model_output" in trace:
        lines.append(f"- Model step (SIMULATED, model.py) returned: `{json.dumps(trace['model_output'])}`")
    if "validation" in trace:
        lines.append(f"- Validation: {trace['validation'] or 'nothing missing or unclear'}")
    if "edits" in trace:
        lines.append(f"- Edits applied: {trace['edits']['applied'] or 'none'}; errors: {trace['edits']['errors'] or 'none'}")
    if "lookup" in trace:
        lookup = trace["lookup"]
        fit = ", ".join(lookup["fit_in_rank_order"]) or "none"
        lines.append(f"- Availability lookup: {lookup['pitches_checked']} pitches checked; "
                     f"suitable and free, in rank order: {fit}")
    lines += ["", "**What it returned**", "", f"> {data['reply']}", ""]
    if data.get("chips"):
        lines.append(f"- Chips: {chips_text(data['chips'])}")
    for question in data.get("questions", []):
        lines.append(f"- Question: {question['text']}")
    if data.get("recommendation"):
        lines.append(f"- Recommended: {card_text(data['recommendation'])}")
    if data.get("alternatives"):
        lines.append("- Other options: " + "; ".join(c["title"] for c in data["alternatives"]))
    if data.get("near_misses"):
        lines.append("- Closest: " + "; ".join(f"{n['pitch']} ({n['why_not']})" for n in data["near_misses"]))
    actions = {"book": "Book (then Confirm)", "change": "tap a chip to change it",
               "other_options": "look at the other options", "answer": "answer the question",
               "rephrase": "ask about a pitch instead", "try_again": "try again later or call reception"}
    lines += ["", "**What the guest can do next:** " +
              " · ".join(actions.get(a, a) for a in data.get("actions", [])), ""]
    return lines


def run_case(case, version):
    original = app.DATA_DIR
    if case.get("data_dir"):
        app.DATA_DIR = os.path.join(ROOT, case["data_dir"])
    steps = case.get("turns_v2", case["turns"]) if version == "v2" else case["turns"]
    state, turns = None, []
    try:
        for step in steps:
            data = app.turn(step.get("message", ""), state, step.get("edits"), version=version)
            state = data.get("state", state)
            turns.append((step, data))
    finally:
        app.DATA_DIR = original
    return turns


def outcome(turns):
    last = turns[-1][1]
    if last.get("recommendation"):
        return f"recommends {last['recommendation']['name']}"
    if last.get("questions"):
        return "asks: " + " / ".join(q["text"] for q in last["questions"])
    return "no pitch: " + last["reply"][:70]


def main():
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(ROOT, "tests", "cases.json"), encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    summary = ["# Test results", "",
               "v1 = the path as first built and tested. v2 = after the Phase 4 changes "
               "(validation step, clarification questions, value + source + evidence per field).", "",
               "| Case | Version | Turns | First turn | After the last turn |", "|---|---|---|---|---|"]
    for case in cases:
        for version in ("v1", "v2"):
            turns = run_case(case, version)
            lines = [f"# {case['title']} ({version})", ""]
            for number, (step, data) in enumerate(turns, 1):
                lines += describe(step, data, number)
            path = os.path.join(RESULTS, f"{case['id']}_{version}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            first = outcome(turns[:1])
            last = outcome(turns) if len(turns) > 1 else "(same)"
            summary.append(f"| {case['title']} | {version} | {len(turns)} | {first} | {last} |")
            print(f"{case['id']:<20} {version}  {first}  ->  {last}")
    with open(os.path.join(RESULTS, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")


if __name__ == "__main__":
    main()
