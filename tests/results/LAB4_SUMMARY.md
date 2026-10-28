# Lab 4 test results

Replayed through `app.turn()` on v3 by `tests/run_lab4.py`, with temporary hold and log files. The browser checks are recorded separately in `02_TEST_RECORD.md`, `tool_log.jsonl` and `screenshots/`.

## Questions answered from the guest information

| Case | Question | Outcome |
|---|---|---|
| Grounded: the guest information answers it | “What time can we arrive?” | answered from 1 Arriving and leaving (2026-10-01, score 0.89) |
| Stale: an old edition ranks first | “What is your cancellation policy?” | answered from 6 Deposits and cancellations (2026-10-01, score 0.87), stale warning shown |
| Unanswerable: not in the guest information | “Is there a swimming pool?” | declined (best score 0.00) |
| Extra: dogs | “Can I bring my dog?” | answered from 4 Dogs (2026-10-01, score 1.13) |
| Extra: hook-up | “Do all pitches have hook-up?” | answered from 3 Electric hook-up (2026-10-01, score 1.67) |
| Extra: deposit | “How much is the deposit?” | answered from 6 Deposits and cancellations (2026-10-01, score 0.82), stale warning shown |
| Extra: campfire (different word from the passage) | “Can we have a campfire?” | answered from 5 Quiet time and site rules (2026-10-01, score 0.69) |
| Extra: wifi (written Wi-Fi in the passage) | “Is there wifi?” | answered from 2 Facilities (2026-10-01, score 0.75) |
| Extra: check-in (no passage uses that word) | “What time is check-in?” | answered from 1 Arriving and leaving (2026-10-01, score 0.42) |
| Supplied corpus: grounded | “When is coursework 1 due?” | answered from 3 Assessment (2026-09-12, score 1.06) |
| Supplied corpus: stale | “What is the late-submission penalty?” | answered from 5.2 Late submission (2026-09-12, score 0.41), stale warning shown |
| Supplied corpus: unanswerable | “Can I use an AI assistant for the project?” | declined (best score 0.00) |

## The hold_pitch tool

| Case | Outcome (log entries in order; holds in the file) |
|---|---|
| Hold after Test A, then confirm | held; holds now: 1 |
| Hold proposed, then cancelled | cancelled; holds now: 0 |
| Invalid request: 21 nights (shape check) | refused (shape); holds now: 0 |
| Invalid request: an argument missing (shape check) | refused (shape); holds now: 0 |
| Request for a pitch that doesn't suit the party (precondition) | refused (permission or precondition); holds now: 0 |
| Pitch taken by another guest between proposal and confirmation (precondition re-checked) | held; refused (permission or precondition); holds now: 1 |
| A second hold in the same session (permission) | held; refused (permission or precondition); holds now: 1 |
| Confirm pressed twice | held; holds now: 1 |
| The same hold asked for again (idempotency) | held; ok; holds now: 1 |
| A pitch held by another guest is not suggested | held; holds now: 1 |

## Image checks (the lab's mock and sample images)

| Case | Outcome |
|---|---|
| Poster image: the answer is visible | 14 November, 12:00 (confidence 0.86) |
| Noticeboard image: refuse | refused: no deadline is visible in this image, and it shows a named person's mark, which I will not read out |

## Regression: the Lab 3 cases on v3

| Lab 3 case | v3 after the last turn | Compared with v2 |
|---|---|---|
| Test A - standard input (the Week 2 normal storyboard) | recommends Pitch 7 | same as v2 |
| Test B - problem input: vague dates, no vehicle length, and Bella could be a person or a pet | recommends Pitch 12 | same as v2 |
| Extra check - the Week 2 failure storyboard message (dates and length given, Bella still ambiguous) | recommends Pitch 12 | same as v2 |
| Extra check - the dog is named clearly, so v2 should not ask about her | recommends Pitch 12 | same as v2 |
| Out-of-scope request | no pitch: Sorry, I can only help you choose a touring or tent pitch at Danygraig | same as v2 |
| Data source unavailable (pitch and booking files can't be read) | no pitch: I can't check which pitches are free right now, so I won't suggest one | same as v2 |
