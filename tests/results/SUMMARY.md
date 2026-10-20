# Test results

v1 = the path as first built and tested. v2 = after the Phase 4 changes (validation step, clarification questions, value + source + evidence per field).

| Case | Version | Turns | First turn | After the last turn |
|---|---|---|---|---|
| Test A - standard input (the Week 2 normal storyboard) | v1 | 1 | recommends Pitch 7 | (same) |
| Test A - standard input (the Week 2 normal storyboard) | v2 | 1 | recommends Pitch 7 | (same) |
| Test B - problem input: vague dates, no vehicle length, and Bella could be a person or a pet | v1 | 2 | recommends Pitch 3 | recommends Pitch 12 |
| Test B - problem input: vague dates, no vehicle length, and Bella could be a person or a pet | v2 | 2 | asks: Which nights exactly? You said “mid August”. (For example: 14–16 Aug) / Is Bella coming as a guest or a pet? | recommends Pitch 12 |
| Extra check - the Week 2 failure storyboard message (dates and length given, Bella still ambiguous) | v1 | 1 | recommends Pitch 7 | (same) |
| Extra check - the Week 2 failure storyboard message (dates and length given, Bella still ambiguous) | v2 | 2 | asks: Is Bella coming as a guest or a pet? | recommends Pitch 12 |
| Extra check - the dog is named clearly, so v2 should not ask about her | v1 | 1 | recommends Pitch 12 | (same) |
| Extra check - the dog is named clearly, so v2 should not ask about her | v2 | 1 | recommends Pitch 12 | (same) |
| Out-of-scope request | v1 | 1 | no pitch: Sorry, I can only help you choose a touring or tent pitch at Danygraig | (same) |
| Out-of-scope request | v2 | 1 | no pitch: Sorry, I can only help you choose a touring or tent pitch at Danygraig | (same) |
| Data source unavailable (pitch and booking files can't be read) | v1 | 1 | no pitch: I can't check which pitches are free right now, so I won't suggest one | (same) |
| Data source unavailable (pitch and booking files can't be read) | v2 | 1 | no pitch: I can't check which pitches are free right now, so I won't suggest one | (same) |
