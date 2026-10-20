# Out-of-scope request (v2)

### Turn 1: the guest types

> Can you book me a table at the pub on Saturday?

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema. For e...
2. `user`: Can you book me a table at the pub on Saturday?

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": {"value": null, "source": "missing", "evidence": ""}, "check_out": {"value": null, "source": "missing", "evidence": ""}, "adults": {"value": null, "source": "missing", "evidence": ""}, "children": {"value": 0, "source": "assumed", "evidence": "no children mentioned"}, "dogs": {"value": 0, "source": "assumed", "evidence": "no dog mentioned"}, "vehicle": {"value": null, "source": "missing", "evidence": ""}, "vehicle_length_m": {"value": null, "source": "missing", "evidence": ""}, "hookup": {"value": false, "source": "assumed", "evidence": "hook-up not mentioned"}, "unclear_names": [], "out_of_scope": "food and drink"}`

**What it returned**

> Sorry, I can only help you choose a touring or tent pitch at Danygraig: your dates, who's coming, your vehicle, hook-up and dogs. For food and drink, please contact reception.


**What the guest can do next:** ask about a pitch instead
