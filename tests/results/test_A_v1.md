# Test A - standard input (the Week 2 normal storyboard) (v1)

### Turn 1: the guest types

> Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema: dates...
2. `user`: Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 0, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true, "out_of_scope": null}`
- Availability lookup: 14 pitches checked; suitable and free, in rank order: Pitch 7, Pitch 3, Pitch 5, Pitch 12, Pitch 14, Pitch 11

**What it returned**

> Here's what I understood. Tap anything that's wrong.

- Chips: `14–16 Aug (2 nights)` `2 adults` `campervan 6 m` `hook-up` `pets: none`
- Recommended: **Pitch 7 – Riverside (hardstanding)**: fits your 6 m campervan (takes up to 8 m); has electric hook-up; no-dogs area; free 14–16 Aug (2 nights). £29 a night, £58 in total
- Other options: Pitch 3 – Orchard (grass); Pitch 5 – Orchard (grass)

**What the guest can do next:** Book (then Confirm) · tap a chip to change it · look at the other options
