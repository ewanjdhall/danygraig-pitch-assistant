# Invalid request: 21 nights (shape check)

- **sends a hand-written hold request: {"pitch": 12, "check_in": "2027-08-14", "check_out": "2027-09-04", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}** (guest-1): I can't hold that: a stay must be 1 to 14 nights (this one is 21). Nothing was held. | tool result: {"status": "refused", "check": "shape", "reason": "a stay must be 1 to 14 nights (this one is 21)"}

**tool_log.jsonl after the case**

```json
{"t": "2026-10-28T06:39", "tool": "hold_pitch", "args": {"pitch": 12, "check_in": "2027-08-14", "check_out": "2027-09-04", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": true}, "confirmed": false, "session": "guest-1", "result": {"status": "refused", "check": "shape", "reason": "a stay must be 1 to 14 nights (this one is 21)"}}
```

**Holds in the file after the case**

```json
[]
```
