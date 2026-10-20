# Extra check - the dog is named clearly, so v2 should not ask about her (v2)

### Turn 1: the guest types

> me and my partner and our dog Bella, 7m motorhome, 3-5 Sept, need hook-up

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema. For e...
2. `user`: me and my partner and our dog Bella, 7m motorhome, 3-5 Sept, need hook-up

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": {"value": "2027-09-03", "source": "stated", "evidence": "3-5 Sept"}, "check_out": {"value": "2027-09-05", "source": "stated", "evidence": "3-5 Sept"}, "adults": {"value": 2, "source": "stated", "evidence": "me and my partner"}, "children": {"value": 0, "source": "assumed", "evidence": "no children mentioned"}, "dogs": {"value": 1, "source": "stated", "evidence": "our dog"}, "vehicle": {"value": "motorhome", "source": "stated", "evidence": "motorhome"}, "vehicle_length_m": {"value": 7.0, "source": "stated", "evidence": "7m"}, "hookup": {"value": true, "source": "stated", "evidence": "hook-up"}, "unclear_names": [], "out_of_scope": null}`
- Validation: nothing missing or unclear
- Availability lookup: 14 pitches checked; suitable and free, in rank order: Pitch 12, Pitch 14, Pitch 11

**What it returned**

> Here's what I understood. Tap anything that's wrong.

- Chips: `3–5 Sep (2 nights)` `2 adults` `motorhome 7 m` `hook-up` `1 dog`
- Recommended: **Pitch 12 – Dog-friendly field (hardstanding)**: fits your 7 m motorhome (takes up to 8 m); has electric hook-up; dogs welcome; free 3–5 Sep (2 nights). £27 a night, £54 in total
- Other options: Pitch 14 – Dog-friendly field (hardstanding); Pitch 11 – Dog-friendly field (grass)

**What the guest can do next:** Book (then Confirm) · tap a chip to change it · look at the other options
