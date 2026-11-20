# Danygraig pitch assistant

An Intelligent Interactive Systems project (University of Birmingham, 2026–27). A guest describes their
trip in their own words; the assistant shows what it understood as chips they can correct, asks about
ambiguity its rules detect, answers questions about the park from its guest information with the source shown, and can
hold a pitch once the guest has confirmed exactly what will be held.

README prose word count: 1423 (whitespace count; fenced code and commands, URLs, Markdown markup and this count line excluded).

All data is made up: this is not the real Danygraig Holiday Park's pitch list, prices, bookings or rules.

## Project status

| Part | Status |
|---|---|
| Chat page, chips that show where each value came from (stated, assumed, unclear) and can be tapped to correct | implemented |
| Clarification questions before searching for detected unclear dates, party, vehicle or names ("plus Bella") | implemented (v2); incomplete detection, see limitations |
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

## Known limitations

- The language-model steps are simulated. Replaying the examples does not measure a live LLM's accuracy or prove that guests notice errors.
- Chips appear alongside a recommendation when no ambiguity is detected. Checking them before a recommendation is not compulsory.
- Lowercase `bella` is missed as an unclear name; an explicit `2028` year is silently treated as `2027`; zero adults can receive a recommendation even though the hold tool rejects that party. These are unfixed bugs, not successful checks.
- Word-overlap retrieval can miss synonyms or answer only part of a question. Its match score is not a probability, and the 0.25 threshold is not independently validated.
- The recommendation-only comparison baseline and participant evaluation remain planned.

The release-preparation checks are recorded in [REVIEW_CHECKS.md](REVIEW_CHECKS.md). They were performed by an AI assistant, not by the student.

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

This upload copy retains the 24 development commits, their dates, file trees, messages and Claude co-authorship. Only author/committer email metadata was replaced with a GitHub no-reply address. The original local project is unchanged. See [HISTORY_MAP.md](HISTORY_MAP.md) for the original-to-upload commit IDs.

**Lab 3, v1 (20 Oct).** The use case comes from my Week 2 storyboards. First prototype [71eab3f](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/71eab3fe98bbcf2e00b219b035a7ebc5b85a995e): the
schema required every field, so "plus Bella … mid August" became 3 adults on dates nobody chose, shown as
certain ([91eb683](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/91eb6833015fed7b679a11541e5f3bcaec21af66), `tests/results/test_B_v1.md`).

**Lab 3, v2 (20 Oct).** [5625fad](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/5625fadda36e41ea4943f2ffac9f8b4dc48ec1a2): every field carries value, source and the guest's words; a validation
step asks about dates, party, vehicle or unclear names before any search; assumed values are orange.
Checked by replaying every case on both versions ([743360c](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/743360c4c794aa7077af973713ca6a3831ca9566)): Test A unchanged, Test B now asks first.

**Lab 4, v3 (28 Oct).** [e870e21](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/e870e21e9eb6bff8df160ffd84d929514fe1d74b) logged and mapped the context (`01_CONTEXT_MAP.md`). [2a15cc2](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/2a15cc21eb810d1392f084cedb173eeb90b60aeb) and
[e28c13b](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/e28c13b4512ad468640f8e402b90eeb981e8fe87) added the guest-information corpus, answers with their sources, the hold tool and the image
checks. [d87548f](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/d87548fa372f9d1c41e63f67998773913e1a1e76) recorded two retrieval failures from the replayed cases (a campfire question answered
from the hook-up passage; "wifi" missed); [e14bcba](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/e14bcba279b1fc836427a9b72f0bac835a186c38) fixed them and recorded the regression the fix
caused on the way. Browser results: `02_TEST_RECORD.md`, `tool_log.jsonl`, `screenshots/lab4/`.

**A2 report (28 Oct).** Capturing the storyboards showed that v3's out-of-scope reply still said "I can
only help you choose a pitch", which stopped being true once v3 could answer questions and hold pitches;
[aa7eb5c](https://github.com/ewanjdhall/danygraig-pitch-assistant/commit/aa7eb5ca882a7c51b89dd00527d4b629e8a94875) makes it say what v3 can do (Amershi et al.'s G1) and adds the case to the tests.

## AI assistance

- **Tool:** Claude (Anthropic, Claude Opus 5.5) in the Claude app, working as an agent in the project
  folder. It wrote most of the code, tests and records, checked the page in a real browser and made the
  commits; every commit it made carries `Co-Authored-By: Claude`.
- **What I asked it for:** to build Lab 3 from my Week 2 storyboards and Lab 4 on top of it, then to
  draft the A2 report with its diagram and storyboards, without submitting anything.
- **Report provenance:** The request above concerned earlier AI-assisted drafts, not the independently written report I intend to submit. I wrote "COPPYY (shortened)" independently from my own notes. AI assistance with the prototype, tests, development records, figures and subsequent review is acknowledged separately.
- **Output that was checked and changed** (details with times in `02_PROMPT_LOG.md`): a live LLM was
  rejected so tests replay exactly and no key is needed; v1's guessing was kept on purpose as evidence;
  the hold confirmation was changed to mark assumed values after a browser check showed "a 6 m campervan"
  that the guest never stated; failing retrieval results were committed before being fixed.
- **My own checks:** On 19 Nov I re-ran the Lab 4 tests on my laptop and the saved results didn't change. Then I tried the four example messages above in the app. It marked the children and dogs I hadn't mentioned as assumed before holding Pitch 7, and asked about Bella and the dates instead of guessing. It also used the 2027 cancellation policy even though the old 2026 page scored higher. One problem: when I said Bella was a guest, it counted her as a third adult without marking that as assumed, though she could be a child. I've left that for Phase 3.
- **Later assistance:** ChatGPT / Codex (OpenAI) reviewed the files and report and prepared this separate repository copy. Its test runs are labelled as assisted checks in `REVIEW_CHECKS.md`. It did not submit coursework, and its actions must not be claimed as the student's personal checks. No application behaviour was changed during repository preparation.

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

## Supplied teaching material

`corpus_supplied/`, `sample_images/`, `vlm.py` and the original retrieval helper come from the module's lab pack. The sample noticeboard explicitly says its name and mark are invented. Dates and weights in these fixtures are teaching examples, not the real IIS assessment brief. Other park data and guest information are fictional too. Reused teaching material is acknowledged, not claimed as original work; this repository does not grant a licence to the module team's material.
