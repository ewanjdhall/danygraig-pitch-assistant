# 01_CONTEXT_MAP.md

Context means all the information the app sends to the model for one request. This map records what
the Danygraig booking assistant actually sends, read from the `CONTEXT:` lines that `log_context(parts)`
prints in the terminal (added in `app.py` in Phase 1). The model step is simulated (`model.py`), but it
receives the same `parts` list a real model would.

## Phase 1: the booking path, as observed (Wed 28 Oct 2026)

Requests made in the browser: "Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up", then
"actually we'll bring our dog too". Terminal output for the second request:

```text
CONTEXT: {'role': 'system', 'content': "You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema. For every field give the value, where it came from (stated by the guest, assumed by you, vague, or missing) and the guest's own words as evidence. Never guess dates or how many people are coming: mark them vague or missing. If a name could be a person or a pet, list it in unclear_names instead of counting it."}
CONTEXT: {'role': 'system', 'content': 'Requirements so far: {"check_in": {"value": "2027-08-14", "source": "stated", "evidence": "14-16 Aug"}, "check_out": {"value": "2027-08-16", "source": "stated", "evidence": "14-16 Aug"}, "adults": {"value": 2, "source": "stated", "evidence": "2 adults"}, "children": {"value": 0, "source": "assumed", "evidence": "no children mentioned"}, "dogs": {"value": 0, "source": "assumed", "evidence": "no dog mentioned"}, "vehicle": {"value": "campervan", "source": "stated", "evidence": "campervan"}, "vehicle_length_m": {"value": 6, "source": "stated", "evidence": "6m"}, "hookup": {"value": true, "source": "stated", "evidence": "electric"}, "unclear_names": []}'}
CONTEXT: {'role': 'user', 'content': "actually we'll bring our dog too"}
```

The first request sent only the instructions and the message. The page then showed Pitch 7 for the
first request and, after the second, "Pitch 7 doesn't work any more (dogs aren't allowed there)" and
Pitch 12.

| part | where it comes from | what kind of information it is | trusted? | size |
|---|---|---|---|---|
| app instructions (`system`) | `SYSTEM_INSTRUCTIONS["v2"]` in `app.py`, sent with every model call | instructions from my app | yes: written by me and kept in Git | short (about 80 words) |
| requirements so far (`system`) | the page keeps the requirements from the last reply and sends them back; `build_parts()` adds them from the second message on | my app's own summary of earlier turns: value, source and the guest's words for each field | partly: my app wrote it, but it comes back through the browser, so a user could change it. `validate()` and the availability lookup re-check the values before anything is suggested | medium (about 110 words); it stays the same size however long the conversation gets |
| current user message (`user`) | the message typed in the browser | user input | no: it is data to extract from, never an instruction to the system | short |
| history (earlier messages) | not present: the requirements summary stands in for the transcript | not present | not present | not present |
| retrieved passages | not present: there is no retrieval yet | not present | not present | not present |
| tool definitions | not present: the model step never proposes an action, and the app builds any action itself | not present | not present | not present |
| environment state (today's date, the season) | not present in the request: the simulated model step takes the 2027 season from `model.py` | not present | not present | not present |
| chip edits | never sent to the model: `apply_edits()` changes the requirements in code, with no model call | not present in the model request | not present | not present |

**Removal decision:** nothing redundant to remove on the booking path. Each part is used: the
instructions, the summary (so the model keeps earlier answers without the whole transcript) and the
new message. The guest's words inside the summary look like repetition, but the chips show them as
"From: …", so removing them would break the visible source of each value.

**One thing I would review after retrieval is added:** whether the requirements summary should still be
sent when the guest asks a question about the park. A rules question does not need their dates, party
or dog.
