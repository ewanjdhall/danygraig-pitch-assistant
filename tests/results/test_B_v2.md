# Test B - problem input: vague dates, no vehicle length, and Bella could be a person or a pet (v2)

### Turn 1: the guest types

> hi, two of us plus Bella in the campervan, need power, mid August

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema. For e...
2. `user`: hi, two of us plus Bella in the campervan, need power, mid August

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": {"value": null, "source": "vague", "evidence": "mid August"}, "check_out": {"value": null, "source": "vague", "evidence": "mid August"}, "adults": {"value": 2, "source": "stated", "evidence": "two of us"}, "children": {"value": 0, "source": "assumed", "evidence": "no children mentioned"}, "dogs": {"value": 0, "source": "assumed", "evidence": "no dog mentioned"}, "vehicle": {"value": "campervan", "source": "stated", "evidence": "campervan"}, "vehicle_length_m": {"value": 6.0, "source": "assumed", "evidence": "no length given; a typical campervan is about 6 m"}, "hookup": {"value": true, "source": "stated", "evidence": "power"}, "unclear_names": [{"name": "Bella", "evidence": "plus Bella"}], "out_of_scope": null}`
- Validation: ['Which nights exactly? You said “mid August”. (For example: 14–16 Aug)', 'Is Bella coming as a guest or a pet?']

**What it returned**

> Here's what I understood so far. Before I look for a pitch:

- Chips: `dates: mid August? (vague)` `2 adults` `Bella: guest or pet? (unclear)` `campervan ~6 m (assumed)` `hook-up`
- Question: Which nights exactly? You said “mid August”. (For example: 14–16 Aug)
- Question: Is Bella coming as a guest or a pet?

**What the guest can do next:** answer the question · tap a chip to change it

### Turn 2: the guest types

> 14-16 Aug, Bella's our dog

*Why: the guest answers the two questions.*

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema. For e...
2. `system`: Requirements so far: {"check_in": {"value": null, "source": "vague", "evidence": "mid August"}, "check_out": {"value": null, "source": "vague", "evidence": "...
3. `user`: 14-16 Aug, Bella's our dog

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": {"value": "2027-08-14", "source": "stated", "evidence": "14-16 Aug"}, "check_out": {"value": "2027-08-16", "source": "stated", "evidence": "14-16 Aug"}, "adults": {"value": 2, "source": "stated", "evidence": "two of us"}, "children": {"value": 0, "source": "assumed", "evidence": "no children mentioned"}, "dogs": {"value": 1, "source": "stated", "evidence": "Bella's our dog"}, "vehicle": {"value": "campervan", "source": "stated", "evidence": "campervan"}, "vehicle_length_m": {"value": 6.0, "source": "assumed", "evidence": "no length given; a typical campervan is about 6 m"}, "hookup": {"value": true, "source": "stated", "evidence": "power"}, "unclear_names": [], "out_of_scope": null}`
- Validation: nothing missing or unclear
- Availability lookup: 14 pitches checked; suitable and free, in rank order: Pitch 12, Pitch 14, Pitch 11

**What it returned**

> Thanks, Bella is down as a dog. Here's what I understood. Tap anything that's wrong. I've assumed the orange ones.

- Chips: `14–16 Aug (2 nights)` `2 adults` `campervan ~6 m (assumed)` `hook-up` `1 dog`
- Recommended: **Pitch 12 – Dog-friendly field (hardstanding)**: takes a campervan up to 8 m (I've assumed yours is about 6 m); has electric hook-up; dogs welcome; free 14–16 Aug (2 nights). £27 a night, £54 in total
- Other options: Pitch 14 – Dog-friendly field (hardstanding); Pitch 11 – Dog-friendly field (grass)

**What the guest can do next:** Book (then Confirm) · tap a chip to change it · look at the other options
