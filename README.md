# Danygraig pitch assistant

An Intelligent Interactive Systems project (University of Birmingham, 2026–27). A guest describes their
trip in their own words; the assistant shows what it understood as chips they can correct, asks before
guessing, answers questions about the park from its guest information with the source shown, and can
hold a pitch once the guest has confirmed exactly what will be held.

README prose: 839 words (code and commands not counted).

All data is made up: this is not the real Danygraig Holiday Park's pitch list, prices, bookings or rules.

## Project status

| Part | Status |
|---|---|
| Chat page, chips that show where each value came from (stated, assumed, unclear) and can be tapped to correct | implemented |
| Clarification questions before searching when dates, party, vehicle or a name ("plus Bella") are unclear | implemented (v2) |
| Availability lookup and ranking over made-up pitches and bookings, with reasons for each suggestion | implemented |
| Questions about the park answered from `corpus/` with the passage, source, section, date and score shown; stale editions flagged; declines below 0.25 | implemented (v3) |
| `hold_pitch` tool: one 48-hour hold, validated, confirmed with its arguments, re-checked, reported from its result, logged | implemented (v3) |
| Language-model steps (`model.py`): a rule-based stand-in with the same interface as a structured-output call | **simulated** |
| Answer step: quotes the chosen passage instead of a model writing the answer | **simulated** |
| Image check (`vlm.py`): the lab's mock with its two sample images | **simulated** |
| Booking, payment and email confirmation (a hold lives only in `data/holds.json`) | **planned** |
| A real LLM, retrieval by meaning rather than words, today's date in the context | **planned** |
| Recommendation-only version for comparison, and a study with users (Assignment 3) | **planned** |

## Technology stack

- Python 3 standard library only (`http.server`); one page, `index.html`, with plain JavaScript. Nothing to install.
- `model.py`: simulated model step behind `call_json(parts, schema)`, with three schemas: v1 (every field required, so it guesses), v2 (value, source and evidence for every field), v3 (v2 plus a `question` field).
- `retrieve.py`: the lab's word-overlap retriever, changed to ignore conversational words, match "Wi-Fi"/"wifi" and fold plurals.
- `hold_tool.py`: the one tool, with the five checks from Lecture 12.
- Still undecided: which model to use for the planned live route; how to choose the retrieval threshold.
- AI tool used to build it: Claude (see AI assistance).

## Running or inspecting the work

```bash
python app.py              # v3, the current version: open http://localhost:8000
python app.py --v2         # Lab 3 after its revision (asks before guessing)
python app.py --v1         # Lab 3 as first built (guesses)
python tests/run_tests.py  # Lab 3 conversations on v1 and v2 -> tests/results/*_v1.md, *_v2.md
python tests/run_lab4.py   # Lab 4 checks on v3, plus every Lab 3 case on v3 -> tests/results/LAB4_SUMMARY.md
python retrieve.py "what is your cancellation policy?"
python hold_tool.py --selftest
```

Things to type: `Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up` (then **Hold this pitch**),
`hi, two of us plus Bella in the campervan, need power, mid August`, `What is your cancellation policy?`,
`Is there a swimming pool?`. "What the system did" under each reply shows the context sent and the
model step's output. No API key is needed. If a live model is added, its key goes in an environment
variable, never in this repository.

## Development record

**Lab 3, v1 (20 Oct).** The use case comes from my Week 2 storyboards. First prototype `20085a0`: the
schema required every field, so "plus Bella … mid August" became 3 adults on dates nobody chose, shown as
certain (`1347664`, `tests/results/test_B_v1.md`).

**Lab 3, v2 (20 Oct).** `6dd844b`: every field carries value, source and the guest's words; a validation
step asks about dates, party, vehicle or unclear names before any search; assumed values are orange.
Checked by replaying every case on both versions (`1d06554`): Test A unchanged, Test B now asks first.

**Lab 4, v3 (28 Oct).** `722ea61` logged and mapped the context (`01_CONTEXT_MAP.md`). `2b576b8` and
`1e3fc2e` added the guest-information corpus, answers with their sources, the hold tool and the image
checks. `4f0afa8` recorded two retrieval failures from the replayed cases (a campfire question answered
from the hook-up passage; "wifi" missed); `0e68bf7` fixed them and recorded the regression the fix
caused on the way. Browser results: `02_TEST_RECORD.md`, `tool_log.jsonl`, `screenshots/lab4/`.

**A2 report (28 Oct).** Capturing the storyboards showed that v3's out-of-scope reply still said "I can
only help you choose a pitch", which stopped being true once v3 could answer questions and hold pitches;
`75ea381` makes it say what v3 can do (Amershi et al.'s G1) and adds the case to the tests.

## AI assistance

- **Tool:** Claude (Anthropic, Claude Opus 5.5) in the Claude app, working as an agent in the project
  folder. It wrote most of the code, tests and records, checked the page in a real browser and made the
  commits; every commit it made carries `Co-Authored-By: Claude`.
- **What I asked it for:** to build Lab 3 from my Week 2 storyboards and Lab 4 on top of it, then to
  draft the A2 report with its diagram and storyboards, without submitting anything.
- **Output that was checked and changed** (details with times in `02_PROMPT_LOG.md`): a live LLM was
  rejected so tests replay exactly and no key is needed; v1's guessing was kept on purpose as evidence;
  the hold confirmation was changed to mark assumed values after a browser check showed "a 6 m campervan"
  that the guest never stated; failing retrieval results were committed before being fixed.
- **My own checks:** [Ewan: add what you ran, read or changed yourself.]

## Additional files

- `01_SPEC.md`: the Lab 3 specification, tests A and B, review and revision.
- `01_CONTEXT_MAP.md`, `02_TEST_RECORD.md`, `tool_log.jsonl`: Lab 4 records. `data/holds.json` is created when a pitch is held and is not kept in Git.
- `02_PROMPT_LOG.md`: AI use for Labs 3 and 4.
- `tests/results/`: every replayed conversation; `screenshots/`: the pages; `diagrams/`: system paths
  (v1, v2) and the A2 system diagram (v3); `storyboard/`: my Week 2 storyboards.
- `storyboard/a2/`: the A2 storyboards, real screenshots captured from the running app by
  `tools/figures/` (these scripts need Playwright; the app itself does not).
- `corpus_supplied/`: the lab's six sample documents, unchanged
  (`python retrieve.py --corpus corpus_supplied "when is coursework 1 due"`).
