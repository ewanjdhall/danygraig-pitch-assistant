# Test A - standard input (the Week 2 normal storyboard) (v2)

### Turn 1: the guest types

> Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema. For e...
2. `user`: Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": {"value": "2027-08-14", "source": "stated", "evidence": "14-16 Aug"}, "check_out": {"value": "2027-08-16", "source": "stated", "evidence": "14-16 Aug"}, "adults": {"value": 2, "source": "stated", "evidence": "2 adults"}, "children": {"value": 0, "source": "assumed", "evidence": "no children mentioned"}, "dogs": {"value": 0, "source": "assumed", "evidence": "no dog mentioned"}, "vehicle": {"value": "campervan", "source": "stated", "evidence": "campervan"}, "vehicle_length_m": {"value": 6.0, "source": "stated", "evidence": "6m"}, "hookup": {"value": true, "source": "stated", "evidence": "electric"}, "unclear_names": [], "out_of_scope": null}`
- Validation: nothing missing or unclear
- Availability lookup: 14 pitches checked; suitable and free, in rank order: Pitch 7, Pitch 3, Pitch 5, Pitch 12, Pitch 14, Pitch 11

**What it returned**

> Here's what I understood. Tap anything that's wrong. I've assumed the orange ones.

- Chips: `14–16 Aug (2 nights)` `2 adults` `campervan 6 m` `hook-up` `pets: none (assumed)`
- Recommended: **Pitch 7 – Riverside (hardstanding)**: fits your 6 m campervan (takes up to 8 m); has electric hook-up; no-dogs area; free 14–16 Aug (2 nights). £29 a night, £58 in total
- Other options: Pitch 3 – Orchard (grass); Pitch 5 – Orchard (grass)

**What the guest can do next:** Book (then Confirm) · tap a chip to change it · look at the other options
