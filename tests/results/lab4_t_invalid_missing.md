# Invalid request: an argument missing (shape check)

- **sends a hand-written hold request: {"pitch": 12, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0}** (guest-1): I can't hold that: the request is missing hookup. Nothing was held. | tool result: {"status": "refused", "check": "shape", "reason": "the request is missing hookup"}

**tool_log.jsonl after the case**

```json
{"t": "2026-10-28T06:39", "tool": "hold_pitch", "args": {"pitch": 12, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0, "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0}, "confirmed": false, "session": "guest-1", "result": {"status": "refused", "check": "shape", "reason": "the request is missing hookup"}}
```

**Holds in the file after the case**

```json
[]
```
