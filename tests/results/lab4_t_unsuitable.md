# Request for a pitch that doesn't suit the party (precondition)

- **sends a hand-written hold request: {"pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}** (guest-1): I can't hold that: dogs aren't allowed on Pitch 7. Nothing was held. | tool result: {"status": "refused", "check": "permission or precondition", "reason": "dogs aren't allowed on Pitch 7"}

**tool_log.jsonl after the case**

```json
{"t": "2026-10-28T06:41", "tool": "hold_pitch", "args": {"pitch": 7, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}, "confirmed": false, "session": "guest-1", "result": {"status": "refused", "check": "permission or precondition", "reason": "dogs aren't allowed on Pitch 7"}}
```

**Holds in the file after the case**

```json
[]
```
