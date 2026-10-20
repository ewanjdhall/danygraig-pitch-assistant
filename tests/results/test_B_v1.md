# Test B - problem input: vague dates, no vehicle length, and Bella could be a person or a pet (v1)

### Turn 1: the guest types

> hi, two of us plus Bella in the campervan, need power, mid August

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema: dates...
2. `user`: hi, two of us plus Bella in the campervan, need power, mid August

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": "2027-08-15", "check_out": "2027-08-17", "adults": 3, "children": 0, "dogs": 0, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true, "out_of_scope": null}`
- Availability lookup: 14 pitches checked; suitable and free, in rank order: Pitch 3, Pitch 5, Pitch 12, Pitch 14, Pitch 11

**What it returned**

> Here's what I understood. Tap anything that's wrong.

- Chips: `15–17 Aug (2 nights)` `3 adults` `campervan 6 m` `hook-up` `pets: none`
- Recommended: **Pitch 3 – Orchard (grass)**: fits your 6 m campervan (takes up to 8 m); has electric hook-up; quiet, no-dogs area; free 15–17 Aug (2 nights). £25 a night, £50 in total
- Other options: Pitch 5 – Orchard (grass); Pitch 12 – Dog-friendly field (hardstanding)

**What the guest can do next:** Book (then Confirm) · tap a chip to change it · look at the other options

### Turn 2: the guest edits chips (dogs → 1 dog, adults → 2)

*Why: the guest spots '3 adults' and 'pets: none' and corrects them.*

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema: dates...
2. `system`: Requirements so far: {"check_in": "2027-08-15", "check_out": "2027-08-17", "adults": 3, "children": 0, "dogs": 0, "vehicle": "campervan", "vehicle_length_m":...
- Chip edits: `{"dogs": "1 dog", "adults": "2"}` (applied in app.py; no model call)

**What it did**

- Edits applied: ['dogs → 1', 'adults → 2']; errors: none
- Availability lookup: 14 pitches checked; suitable and free, in rank order: Pitch 12, Pitch 14, Pitch 11

**What it returned**

> Updated: dogs → 1, adults → 2. Pitch 3 doesn't work any more (dogs aren't allowed there), so here's another. Here's what I understood. Tap anything that's wrong.

- Chips: `15–17 Aug (2 nights)` `2 adults` `campervan 6 m` `hook-up` `1 dog`
- Recommended: **Pitch 12 – Dog-friendly field (hardstanding)**: fits your 6 m campervan (takes up to 8 m); has electric hook-up; dogs welcome; free 15–17 Aug (2 nights). £27 a night, £54 in total
- Other options: Pitch 14 – Dog-friendly field (hardstanding); Pitch 11 – Dog-friendly field (grass)

**What the guest can do next:** Book (then Confirm) · tap a chip to change it · look at the other options
