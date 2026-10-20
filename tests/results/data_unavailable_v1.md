# Data source unavailable (pitch and booking files can't be read) (v1)

### Turn 1: the guest types

> Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up

**What the system received**

1. `system`: You are the booking assistant for Danygraig Holiday Park. Read the guest's message and return their pitch requirements as JSON that matches the schema: dates...
2. `user`: Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up

**What it did**

- Loading the pitch data failed: `[Errno 2] No such file or directory: '/home/claude/lab3/lab3_pack/missing-folder/pitches.json'`. No model call and no lookup.

**What it returned**

> I can't check which pitches are free right now, so I won't suggest one. Please try again later or call reception.


**What the guest can do next:** try again later or call reception
