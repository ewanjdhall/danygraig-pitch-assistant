# Pitch taken by another guest between proposal and confirmation (precondition re-checked)

- **says “hi, two of us plus Bella in the campervan, need power, mid August”** (guest-1): Here's what I understood so far. Before I look for a pitch:
- **says “14-16 Aug, Bella's our dog”** (guest-1): Thanks, Bella is down as a dog. Here's what I understood. Tap anything that's wrong. I've assumed the orange ones. | recommends Pitch 12
- **presses Hold this pitch on Pitch 12** (guest-1): Please check this before I hold the pitch. | Hold Pitch 12 (Dog-friendly field, hardstanding) for 2 nights, Sat 14 Aug to Mon 16 Aug 2027, for 2 adults and 1 dog with a campervan of about 6 m (I assumed the length), with hook-up? The hold lasts 48 hours and keeps the pitch for you. Nothing is paid (the stay would cost £54), no booking is confirmed and nobody is contacted.
- **says “me and my partner and our dog Bella, 7m motorhome, 15-17 Aug, need hook-up”** (guest-2): Here's what I understood. Tap anything that's wrong. | recommends Pitch 12
- **presses Hold this pitch on Pitch 12** (guest-2): Please check this before I hold the pitch. | Hold Pitch 12 (Dog-friendly field, hardstanding) for 2 nights, Sun 15 Aug to Tue 17 Aug 2027, for 2 adults and 1 dog with a 7 m motorhome, with hook-up? The hold lasts 48 hours and keeps the pitch for you. Nothing is paid (the stay would cost £54), no booking is confirmed and nobody is contacted.
- **presses Hold Pitch (confirm)** (guest-2): Held: Pitch 12 for 15–17 Aug 2027 (hold H-0001), until Fri 30 Oct, 09:00. Nothing has been paid and no booking is confirmed. In the real system, reception would confirm the booking and take the deposit. | tool result: {"status": "held", "hold_id": "H-0001", "pitch": 12, "check_in": "2027-08-15", "check_out": "2027-08-17", "expires": "2026-10-30T09:00", "active_holds": 1}
- **presses Hold Pitch (confirm)** (guest-1): I couldn't hold it: Pitch 12 has just been held by another guest for some of those nights. Nothing was held. | tool result: {"status": "refused", "check": "permission or precondition", "reason": "Pitch 12 has just been held by another guest for some of those nights"}

**tool_log.jsonl after the case**

```json
{"t": "2026-10-28T09:00", "tool": "hold_pitch", "args": {"pitch": 12, "check_in": "2027-08-15", "check_out": "2027-08-17", "adults": 2, "children": 0, "dogs": 1, "vehicle": "motorhome", "vehicle_length_m": 7.0, "hookup": true}, "confirmed": true, "session": "guest-2", "result": {"status": "held", "hold_id": "H-0001", "pitch": 12, "check_in": "2027-08-15", "check_out": "2027-08-17", "expires": "2026-10-30T09:00", "active_holds": 1}}
{"t": "2026-10-28T09:00", "tool": "hold_pitch", "args": {"pitch": 12, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}, "confirmed": true, "session": "guest-1", "result": {"status": "refused", "check": "permission or precondition", "reason": "Pitch 12 has just been held by another guest for some of those nights"}}
```

**Holds in the file after the case**

```json
[
 {
  "id": "H-0001",
  "pitch": 12,
  "check_in": "2027-08-15",
  "check_out": "2027-08-17",
  "session": "guest-2"
 }
]
```
