# 02_TEST_RECORD.md

Three questions asked in the browser on Wed 28 Oct 2026 (v3, `python app.py`), and what the screen
actually showed. The corpus is the park's guest information in `corpus/` (seven short documents, all
made up for this prototype, including a superseded 2026 edition of the cancellations section).
Screenshots: `screenshots/lab4/q1_grounded.png`, `q2_stale.png` and `q3_unanswerable.png`.

| question | type | what the screen showed | supported? | what I would change |
|---|---|---|---|---|
| "What time can we arrive?" | grounded | "From the guest information 2027, section 1 Arriving and leaving (updated 1 Oct 2026):" and the quoted passage "Arrival time: you can arrive from 2 pm on your arrival day. Please leave your pitch by 11 am on the day you go home." Beside it: that passage marked "Used for the answer", source Guest information 2027 (made-up), section 1, updated 2026-10-01, score 0.89; also the quiet-time passage (0.51) and the deposit passage (0.48) | yes | Nothing for this question. But it only works because the passage says "Arrival time": "What time is check-in?" ties at 0.42 between the arrival and quiet-time passages, and is answered from arrival only because that passage comes first. I would match meaning rather than words (embeddings, or a short list of synonyms such as check-in = arrival) |
| "What is your cancellation policy?" | stale | The retriever ranked the superseded 2026 passage first (score 1.11, "cancel up to 7 days before you arrive"). The page warned: "The top match is from the guest information 2026 (updated 3 Nov 2025), which has been replaced. I've answered from the current guest information 2027 (updated 1 Oct 2026). Both are shown below." The answer quoted the 2027 passage (28 days, score 0.87); the 2026 passage stayed visible, marked SUPERSEDED and struck through | partly: the answer and the warning are right, but the ranking is still wrong | Rank superseded passages below any current passage from the same section before choosing the top three, and keep them only for comparison. Better still, the park would remove the 2026 edition: the code can only work around an out-of-date corpus |
| "Is there a swimming pool?" | unanswerable | "The park information I have doesn't answer that, so I won't guess. Please ask reception." and "Best match scored 0.00; I only answer from passages scoring 0.25 or more, so no passage is shown as evidence." No passages shown | yes | Nothing for this question. The 0.25 threshold is the lab's value: on my corpus the weakest right answer scored 0.42 (check-in) and, before the retrieval fix below, a wrong passage scored 0.46 (campfire), so the threshold alone could not tell them apart. I would test more questions before trusting it |

## Other checks in the browser (same session)

| check | what the screen showed | right? |
|---|---|---|
| Hold a pitch (Test A, then "Hold this pitch" on Pitch 7) | A confirmation, not "Are you sure?": "Hold Pitch 7 (Riverside, hardstanding) for 2 nights, Sat 14 Aug to Mon 16 Aug 2027, for 2 adults with a 6 m campervan, with hook-up?", the arguments listed (children and dogs marked "assumed"), and "The hold lasts 48 hours… Nothing is paid (the stay would cost £58), no booking is confirmed and nobody is contacted." After "Hold Pitch 7": "Held: Pitch 7 for 14–16 Aug 2027 (hold H-0001)…" and the tool's result `{"status":"held","hold_id":"H-0001",…}`. The first line of `tool_log.jsonl` has the tool name, arguments, `"confirmed": true` and the same result | yes |
| Invalid request ("Lab 4 checks" → 21 nights) | "I can't hold that: a stay must be 1 to 14 nights (this one is 21). Nothing was held." and the tool result `{"status":"refused","check":"shape",…}`. Logged with `"confirmed": false`; `data/holds.json` still holds only H-0001 | yes |
| Cancel (Test B, then Hold Pitch 12, then Cancel) | The confirmation said "a campervan of about 6 m (I assumed the length)"; after Cancel: "Cancelled. Nothing was held." Logged as `{"status": "cancelled"}` | yes |
| Image with the answer (`sample_poster.png`, "what deadline is shown?") | "14 November, 12:00" with a "confidence 0.86" badge and "Evidence: the sheet reads 'Due: 14 November, 12:00'" | yes |
| Image that can't support it (`sample_noticeboard.png`) | "I can't answer that from this image." and "Refused: no deadline is visible in this image, and it shows a named person's mark, which I will not read out". No date and no mark shown | yes |

The images are the lab's two samples run through the lab's mock (`vlm.py`). They sit under "Lab 4 checks"
because a guest would not send a course poster; a planned use in this project is reading a van's length
from a photo of its specification plate, shown as an assumed value with its confidence.

## Retrieval problems found and fixed (from `tests/run_lab4.py`)

| question | before (supplied scoring) | after the fix | change made |
|---|---|---|---|
| "Can we have a campfire?" | **no**: answered from the hook-up passage ("Pitches 1, 4 and 13 have no hook-up.", 0.46), matched only on "can", "we" and "have", a false alarm above the threshold | answered from the site rules ("Open fires, campfires and fire pits are not allowed.", 0.69) | `retrieve.py` no longer scores words guests put in every question ("can", "we", "have", "do", "I" …), and folds simple plurals; the site-rules passage now uses the guest's word, "campfires" |
| "Is there wifi?" | declined at 0.00, because the passage says "Wi-Fi": a miss, but a safe one | answered from the facilities passage (0.75) | "Wi-Fi" and "hook-up" also count as "wifi" and "hookup" |
| "What time can we arrive?" | 0.57, right | **broke** after the stop-word change alone: answered from the quiet-time passage (0.59), because "time" was the strongest word left. Fixed by starting the passage "Arrival time:" (0.89) | caught by rerunning all the cases; shows why every case is rerun after a change |

## The supplied corpus, for comparison

The lab's six documents are kept in `corpus_supplied/`. Through the same answer code
(`tests/results/lab4_q_supplied_*.md`): "When is coursework 1 due?" answered from §3 at 1.06;
"What is the late-submission penalty?" ranked the 2024 handbook first (0.71), warned, and answered from
the 2026 rule (0.41); "Can I use an AI assistant for the project?" scored 0.00 everywhere and declined.
That matches the staff reference, except that my retrieval change lowers some scores (0.82 and 0.49 in
the reference).
