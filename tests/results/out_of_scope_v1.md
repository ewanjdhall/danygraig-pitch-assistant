# Out-of-scope request (v1)

### Turn 1: the guest types

> Can you book me a table at the pub on Saturday?

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema: dates...
2. `user`: Can you book me a table at the pub on Saturday?

**What it did**

- Model step (SIMULATED, model.py) returned: `{"check_in": "2027-03-05", "check_out": "2027-03-07", "adults": 2, "children": 0, "dogs": 0, "vehicle": "tent", "vehicle_length_m": 0.0, "hookup": false, "out_of_scope": "food and drink"}`

**What it returned**

> Sorry, I can only help you choose a touring or tent pitch at Danygraig: your dates, who's coming, your vehicle, hook-up and dogs. For food and drink, please contact reception.


**What the guest can do next:** ask about a pitch instead
