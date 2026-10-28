# 02_PROMPT_LOG.md

I used an AI assistant for this lab. The assistant was Claude (Anthropic, model Claude Opus 5.5), working in the Claude app with access to my course folder. It read the files, wrote and ran the code and the tests, and made the Git commits; every commit made with it carries a `Co-Authored-By: Claude` line. All times are BST on Tue 20 Oct 2026.

## 16:50  Set-up and choice of route
Tool used: Claude (Claude app, agent with access to my project folder).
Request or command: my request was "can u do lab 3 … dont submit anything yet". Claude read the Lab 3 page, the Canvas submission instructions, the Lab 4 page (so the Lab 3 app would work as Lab 4's starting point), the `lab3_pack` starter files and my Week 2 worksheet and storyboards.
What came back: it chose the prototype route, used the use case from my Week 2 storyboard (a guest describes their trip and gets a pitch suggested), and committed the starter pack unchanged as the first Git commit.
What I decided to keep, change or reject, and why:
- **Kept:** the layout Lab 4 expects (`app.py` with `turn(message)` → `model.call_json(parts, SCHEMA)`, `index.html` with `render(data)`, served by `python app.py` on port 8000).
- **Rejected:** a live LLM API. API keys must not go in the project, and a live model would make Test A and Test B hard to repeat exactly. The model step is simulated instead and labelled as simulated everywhere.

## 16:55  Made-up data and the v1 prototype
Tool used: Claude.
Request or command: build the v1 system path from the storyboard. The page sends the message, the model step extracts the requirements, the app looks up free pitches, ranks them and shows chips and a recommended pitch, and Book → Confirm.
What came back:
- `data/pitches.json` and `data/bookings.json`: 14 pitches and 7 bookings, all made up, set so the results match my storyboards (Pitch 7 for Alex, Pitch 3 in the no-dogs area, Pitch 12 dog-friendly);
- `app.py`, `model.py` and `index.html`.

In v1, `model.py` behaves like a model whose schema requires every field, so it guesses anything missing.
What I decided to keep, change or reject, and why:
- **Kept:** the guessing behaviour on purpose. It is what my Week 2 failure storyboard predicted, and Test B needed to show it.
- **Kept:** Python's standard library only, so `python app.py` works with no installs.
- **Rejected:** using the real Danygraig pitch list or prices. The data is made up.

## 17:00  Test A and Test B on v1
Tool used: Claude.
Request or command: run Test A ("Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up") and Test B ("hi, two of us plus Bella in the campervan, need power, mid August"), record what the system received, did, returned and offered next, and take screenshots.
What came back:
- `tests/run_tests.py`, `tests/cases.json` and `tests/results/*_v1.md`;
- `screenshots/v1_test_A.png` and `screenshots/v1_test_B.png`.

Test A gave Pitch 7, as in the storyboard. Test B gave Pitch 3, a no-dogs pitch, for guessed dates (15–17 Aug) and 3 adults, all shown as if they were certain.
What I decided to keep, change or reject, and why:
- **Kept:** both results unchanged, as evidence for the review.
- **Added:** an out-of-scope case and a missing-data case, to answer the review questions about scope and honesty.

## 17:02  Spec and system-path diagram (v1)
Tool used: Claude.
Request or command: fill in `01_SPEC.md` (goal, inputs, processing and technology, result, fallback, Tests A and B) and draw the system path, marking what is implemented, simulated and planned.
What came back: the spec, and `diagrams/system_path_v1.svg` / `.png`, drawn as SVG and exported to PNG.
What I decided to keep, change or reject, and why: **Kept:** the colour coding (green implemented, orange simulated, grey planned), because the lab asks to distinguish these. **Changed:** the label positions after the first export, where some text overlapped.

## 17:05  Phase 3 review and Phase 4 changes (v2)
Tool used: Claude.
Request or command: answer the six review questions with evidence from the tests. Then make one interaction change and one technology change for the main problem and rerun Test B.
What came back:
- **Review:** the main problem is guessing. The v1 schema can't say "unknown", and nothing checks the requirements before the lookup.
- **Interaction change:** clarification questions (at most two, with quick replies for "Is Bella a guest or a pet?"), plus orange "assumed" and dashed "?" chips.
- **Technology change:** a schema with value + source + evidence for every field, plus `unclear_names`; new model instructions; and a `validate()` step before the lookup.
- **Comparison:** v1 is kept behind `python app.py --v1`.
What I decided to keep, change or reject, and why:
- **Kept:** asking only about dates, party, vehicle and unclear names, and showing the rest (length, pets, hook-up) as assumptions. Asking about everything would slow down clear requests like Test A.
- **Rejected:** asking about pets in every conversation, for the same reason.

## 17:08  Rerun and checks
Tool used: Claude.
Request or command: rerun every case on v1 and v2 and check the v1 results are unchanged, then add extra checks: the Week 2 failure message, and a clearly named dog, to make sure v2 doesn't over-ask.
What came back:
- `tests/results/*_v2.md`, `SUMMARY.md`, and v2 screenshots.
- **Test B (v2)** asks two questions, then gives Pitch 12 for 14–16 Aug.
- **Test A** still gives Pitch 7 in one turn.
- The v1 results were identical before and after the change.
- **Browser click-through:** quick reply, chip edit and Book → Confirm all worked, with no console errors.
What I decided to keep, change or reject, and why: **Kept:** the extra checks in `tests/cases.json`, so the "plus <name>" problem stays fixed (a lesson from my Week 2 storyboard).

## 17:10  Updated spec, v2 diagram and storyboard
Tool used: Claude.
Request or command: write up the revision and the Test B rerun, draw the v2 diagram, and add my Week 2 storyboard to the folder.
What came back: the Review and revision section of `01_SPEC.md`, `diagrams/system_path_v2.*`, and `storyboard/` (copied from my Week 2 work).
What I decided to keep, change or reject, and why: **Kept:** the limitation that the model step is simulated, stated plainly in the spec, the app and the page, so nobody mistakes the tests for an evaluation of a real LLM.

---

# Lab 4: AI use (Wed 28 Oct 2026, GMT)

Same assistant: Claude (Anthropic, Claude Opus 5.5) in the Claude app, with access to my course folder.
It read the Lab 4 page, the student handout, the integration steps and the starter files, wrote and ran
the code and the tests, drove a real browser to check the page, and made the Git commits (each carries a
`Co-Authored-By: Claude` line). The supplied mock and sample files were used throughout; no API key, no
live model and no real personal data.

## 06:25  Starting point
Request: "u might have to do lab 3-4 yourself first" (Lab 3 had been done on 20 Oct, so only Lab 4 was needed).
What came back: the Lab 3 app was copied with its Git history into a new folder and run first: Test A
still gave Pitch 7. The Lab 4 support files were added unchanged and the three self-tests passed.
Kept, changed or rejected:
- **Kept:** my Lab 3 app files, as the lab asks, rather than the supplied appointment app.
- **Rejected:** the supplied `mock_model.py` and `recorded_runs/`, which answer for the appointment app.

## 06:29  Phase 1: context
What came back: `log_context(parts)` before the model call, and `01_CONTEXT_MAP.md` filled in from the
real terminal output.
Kept, changed or rejected: **Kept** "nothing redundant to remove" for the booking path, with the
requirements summary marked as only partly trusted because it travels through the browser.

## 06:31  Phase 2: my own corpus and the answer path
What came back: seven made-up guest-information documents for the park (with a superseded 2026
cancellations section for the stale case), question routing in `model.py`, and `answer_turn()` with the
evidence card, the stale warning and the decline below 0.25.
Kept, changed or rejected:
- **Kept:** quoting the passage word for word as the simulated answer, so the answer cannot say more
  than its source; a model writing the answer is labelled as planned.
- **Changed:** the supplied course documents moved to `corpus_supplied/` (still runnable with
  `--corpus`), because a holiday-park assistant should not answer coursework questions.
- **Changed:** the cancellation policy is now a question the assistant can answer; only cancelling *a
  booking* stays out of scope.
- **Rejected:** sending the booking requirements to the answer step (see the context map).

## 06:35  Phase 3: a tool of my own
What came back: `hold_tool.py` (`hold_pitch`) instead of the revision-slot tool, wired to a "Hold this
pitch" button, a confirmation with the arguments, `run()` only after the guest presses "Hold Pitch N",
and `tool_log.jsonl`.
Kept, changed or rejected:
- **Kept:** the app, not the model, builds the call from the chips and the pitch the guest chose, so
  text in a message or a passage can never start it.
- **Changed after the first browser run:** the confirmation said "a 6 m campervan" when I had never given
  a length (Test B). It now says "a campervan of about 6 m (I assumed the length)" and marks assumed
  values, because the guest is approving those arguments.
- **Added:** every check runs again when the hold runs, and holds by other guests are left out of
  suggestions; otherwise the assistant could suggest a pitch that it would then refuse to hold.

## 06:36  Phase 4: images
What came back: two "Lab 4 checks" buttons that run `vlm.py` on the sample images and show the claim
with its confidence, or the refusal with its reason.
Kept, changed or rejected: **Kept** them out of the guest conversation, labelled as lab checks, because
the sample images are a course poster and a noticeboard.

## 06:38  Tests, a failure, and the fix
What came back: `tests/run_lab4.py` replays 12 question cases, 11 tool cases, both images and every Lab 3
case on v3. It found "Can we have a campfire?" answered from the hook-up passage (a false alarm on
"can", "we", "have") and "Is there wifi?" missed ("Wi-Fi").
Kept, changed or rejected:
- **Kept:** the failing results in a commit of their own, before fixing them, as evidence.
- **Changed:** stop words, hyphen joining and plural folding in `retrieve.py`. Rerunning the cases showed
  this broke the grounded case ("What time can we arrive?" went to the quiet-time passage), so the
  arrival passage was reworded to start "Arrival time:", and "campfires" was added to the site rules.
- **Kept as a known weakness:** "What time is check-in?" (a 0.42 tie).

## 06:40  Browser checks and records
What came back: screenshots in `screenshots/lab4/`, `tool_log.jsonl` from the browser session, and
`02_TEST_RECORD.md` written from what the screen showed (including "partly" for the stale case, as the
handout suggests).
