# The same hold asked for again (idempotency)

- **says “Hi, 2 adults, 6m campervan, 14-16 Aug, need electric hook-up”** (guest-1): Here's what I understood. Tap anything that's wrong. I've assumed the orange ones. | recommends Pitch 7
- **presses Hold this pitch on Pitch 7** (guest-1): Please check this before I hold the pitch. | Hold Pitch 7 (Riverside, hardstanding) for 2 nights, Sat 14 Aug to Mon 16 Aug 2027, for 2 adults with a 6 m campervan, with hook-up? The hold lasts 48 hours and keeps the pitch for you. Nothing is paid (the stay would cost £58), no booking is confirmed and nobody is contacted.
- **presses Hold Pitch (confirm)** (guest-1): Held: Pitch 7 for 14–16 Aug 2027 (hold H-0001), until Fri 30 Oct, 06:41. Nothing has been paid and no booking is confirmed. In the real system, reception would confirm the booking and take the deposit. | tool result: {"status": "held", "hold_id": "H-0001", "pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "expires": "2026-10-30T06:41", "active_holds": 1}
- **presses Hold this pitch on Pitch 7** (guest-1): Please check this before I hold the pitch. | Hold Pitch 7 (Riverside, hardstanding) for 2 nights, Sat 14 Aug to Mon 16 Aug 2027, for 2 adults with a 6 m campervan, with hook-up? The hold lasts 48 hours and keeps the pitch for you. Nothing is paid (the stay would cost £58), no booking is confirmed and nobody is contacted.
- **presses Hold Pitch (confirm)** (guest-1): You already hold Pitch 7 for those nights (hold H-0001), so nothing was added. | tool result: {"status": "ok", "hold_id": "H-0001", "pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "expires": "2026-10-30T06:41", "note": "you already hold this; nothing was added"}

**tool_log.jsonl after the case**

```json
{"t": "2026-10-28T06:41", "tool": "hold_pitch", "args": {"pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 0, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}, "confirmed": true, "session": "guest-1", "result": {"status": "held", "hold_id": "H-0001", "pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "expires": "2026-10-30T06:41", "active_holds": 1}}
{"t": "2026-10-28T06:41", "tool": "hold_pitch", "args": {"pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 0, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}, "confirmed": true, "session": "guest-1", "result": {"status": "ok", "hold_id": "H-0001", "pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "expires": "2026-10-30T06:41", "note": "you already hold this; nothing was added"}}
```

**Holds in the file after the case**

```json
[
 {
  "id": "H-0001",
  "pitch": 7,
  "check_in": "2027-08-14",
  "check_out": "2027-08-16",
  "session": "guest-1"
 }
]
```
