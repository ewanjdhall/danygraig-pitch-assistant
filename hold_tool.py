"""hold_tool.py - the one tool the Danygraig assistant can use (Lab 4, Phase 3).

    python hold_tool.py --selftest

hold_pitch places ONE provisional hold on ONE pitch for the given nights, in a local file
(data/holds.json). It takes no payment, confirms no booking and contacts nobody, and a hold lasts
48 hours. It cannot touch anything outside this folder.

It follows the five checks from Lecture 12, all in code rather than in the prompt:
  1. shape         valid(call): every argument present, of the right type and within its limits
  2. permission    one hold at a time for each browser session (there are no accounts in the prototype)
  3. precondition  the pitch exists, still suits the party and is still free on every night,
                   checked again against the files when the hold runs, not when it was suggested
  4. confirmation  describe(call) shows the pitch, nights, party and consequence; run() is only called
                   after the guest presses the confirm button
  5. idempotency   an identical hold that already exists is reported, not added twice
Every call is logged to tool_log.jsonl: refused, cancelled or run.

The model never proposes this call. The app builds it from the requirements the guest has seen as
chips and the pitch the guest chose, so the decision to act stays with the guest.
"""
import json
import os
import re
import sys
import threading
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DANYGRAIG_DATA_DIR", os.path.join(HERE, "data"))
HOLDS = os.environ.get("DANYGRAIG_HOLDS", os.path.join(HERE, "data", "holds.json"))
LOG = os.environ.get("DANYGRAIG_TOOL_LOG", os.path.join(HERE, "tool_log.jsonl"))

TOOL = {
    "name": "hold_pitch",
    "description": ("Place one provisional 48-hour hold on one pitch for the given nights. Takes no "
                    "payment, confirms no booking and contacts nobody."),
    "args": {"pitch": "pitch number 1-14", "check_in": "YYYY-MM-DD", "check_out": "YYYY-MM-DD",
             "adults": "1-6", "children": "0-6", "dogs": "0-2",
             "vehicle": "tent, campervan, motorhome or caravan", "vehicle_length_m": "0-12",
             "hookup": "true or false"},
}
NEEDS_CONFIRMATION = True  # other guests would see the pitch as taken, so a person must agree first
HOLD_HOURS = 48
MAX_NIGHTS = 14
SEASON_START, SEASON_END = date(2027, 3, 1), date(2027, 10, 31)
VEHICLES = ("tent", "campervan", "motorhome", "caravan")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_LOCK = threading.Lock()


# --------------------------------------------------------------------------------------------
# Check 1: shape
# --------------------------------------------------------------------------------------------

def _int_in(args, name, low, high):
    value = args.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        return f"{name} must be a whole number from {low} to {high}"
    return ""


def valid(call):
    """Check the call's shape. Returns (ok, reason); the reason is worded so a guest can be shown it."""
    if not isinstance(call, dict) or call.get("name") != TOOL["name"]:
        return False, "this is not a hold_pitch request"
    a = call.get("arguments")
    if not isinstance(a, dict):
        return False, "the request has no arguments"
    missing = [name for name in TOOL["args"] if name not in a]
    if missing:
        return False, "the request is missing " + ", ".join(missing)
    reason = _int_in(a, "pitch", 1, 99)
    if reason:
        return False, reason
    for name in ("check_in", "check_out"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(a[name])):
            return False, f"{name} must be a date written YYYY-MM-DD"
    try:
        check_in, check_out = date.fromisoformat(a["check_in"]), date.fromisoformat(a["check_out"])
    except ValueError:
        return False, "the dates are not real dates"
    nights = (check_out - check_in).days
    if not 1 <= nights <= MAX_NIGHTS:
        return False, f"a stay must be 1 to {MAX_NIGHTS} nights (this one is {nights})"
    if check_in < SEASON_START or check_out > SEASON_END + timedelta(days=1):
        return False, "the park is open 1 Mar to 31 Oct 2027 in this prototype"
    for name, low, high in (("adults", 1, 6), ("children", 0, 6), ("dogs", 0, 2)):
        reason = _int_in(a, name, low, high)
        if reason:
            return False, reason
    if a["vehicle"] not in VEHICLES:
        return False, "vehicle must be a tent, campervan, motorhome or caravan"
    length = a["vehicle_length_m"]
    if not isinstance(length, (int, float)) or isinstance(length, bool) or not 0 <= length <= 12:
        return False, "vehicle_length_m must be a number of metres from 0 to 12"
    if not isinstance(a["hookup"], bool):
        return False, "hookup must be true or false"
    return True, ""


# --------------------------------------------------------------------------------------------
# Files: pitches and bookings (read only) and holds (the only file this tool writes)
# --------------------------------------------------------------------------------------------

def _read(path, key):
    with open(path, encoding="utf-8") as f:
        return json.load(f)[key]


def _load_holds():
    if not os.path.exists(HOLDS):
        return []
    with open(HOLDS, encoding="utf-8") as f:
        return json.load(f).get("holds", [])


def _save_holds(holds):
    with open(HOLDS, "w", encoding="utf-8") as f:
        json.dump({"_note": "Provisional holds made by the prototype's hold_pitch tool. Made-up data.",
                   "holds": holds}, f, indent=1)


def _active(holds, now):
    return [h for h in holds if datetime.fromisoformat(h["expires"]) > now]


def _overlaps(a_in, a_out, b_in, b_out):
    return a_in < b_out and b_in < a_out


def _short_range(check_in, check_out):
    if check_in.month == check_out.month:
        return f"{check_in.day}–{check_out.day} {MONTHS[check_in.month - 1]}"
    return f"{check_in.day} {MONTHS[check_in.month - 1]} – {check_out.day} {MONTHS[check_out.month - 1]}"


# --------------------------------------------------------------------------------------------
# Checks 2 and 3: permission and precondition, against the files as they are now
# --------------------------------------------------------------------------------------------

def check_now(call, session, now=None):
    """Return (ok, reason, pitch). Run when the hold is proposed and again when it runs."""
    now = now or datetime.now()
    a = call["arguments"]
    try:
        pitches = _read(os.path.join(DATA_DIR, "pitches.json"), "pitches")
        bookings = _read(os.path.join(DATA_DIR, "bookings.json"), "bookings")
        holds = _load_holds()
    except (OSError, ValueError, KeyError):
        return False, "I can't read the pitch, booking or hold files right now", None
    pitch = next((p for p in pitches if p["id"] == a["pitch"]), None)
    if pitch is None:
        return False, f"there is no Pitch {a['pitch']}", None
    check_in, check_out = date.fromisoformat(a["check_in"]), date.fromisoformat(a["check_out"])
    active = _active(holds, now)
    mine = [h for h in active if h["session"] == session]
    same = [h for h in mine if h["pitch"] == a["pitch"] and h["check_in"] == a["check_in"]
            and h["check_out"] == a["check_out"]]
    if mine and not same:  # check 2, permission
        h = mine[0]
        return False, (f"you already hold Pitch {h['pitch']} for "
                       f"{_short_range(date.fromisoformat(h['check_in']), date.fromisoformat(h['check_out']))}, "
                       "and this prototype allows one hold at a time"), pitch
    # check 3, preconditions: does the pitch still suit the party, and is it still free?
    if pitch.get("tents_only") and a["vehicle"] != "tent":
        return False, f"Pitch {pitch['id']} is for tents only", pitch
    if a["vehicle"] == "tent" and pitch["surface"] == "hardstanding":
        return False, f"Pitch {pitch['id']} is hardstanding, not for tents", pitch
    if a["vehicle"] != "tent" and a["vehicle_length_m"] > pitch["max_length_m"]:
        return False, f"Pitch {pitch['id']} takes vehicles up to {pitch['max_length_m']:g} m", pitch
    if a["hookup"] and not pitch["hookup"]:
        return False, f"Pitch {pitch['id']} has no electric hook-up", pitch
    if a["dogs"] and not pitch["dogs"]:
        return False, f"dogs aren't allowed on Pitch {pitch['id']}", pitch
    if a["adults"] + a["children"] > pitch["max_guests"]:
        return False, f"Pitch {pitch['id']} takes up to {pitch['max_guests']} people", pitch
    for b in bookings:
        if b["pitch"] == pitch["id"] and _overlaps(check_in, check_out, date.fromisoformat(b["check_in"]),
                                                   date.fromisoformat(b["check_out"])):
            return False, (f"Pitch {pitch['id']} is booked "
                           f"{_short_range(date.fromisoformat(b['check_in']), date.fromisoformat(b['check_out']))}"), pitch
    for h in active:
        if h["session"] != session and h["pitch"] == pitch["id"] and _overlaps(
                check_in, check_out, date.fromisoformat(h["check_in"]), date.fromisoformat(h["check_out"])):
            return False, f"Pitch {pitch['id']} has just been held by another guest for some of those nights", pitch
    return True, "", pitch


# --------------------------------------------------------------------------------------------
# Check 4: what the confirmation shows
# --------------------------------------------------------------------------------------------

def _plural(n, word, plural=None):
    return f"{n} {word if n == 1 else (plural or word + 's')}"


def describe(call, pitch, assumed=()):
    """The pitch, the nights, the party and the consequence, in words: not 'hold_pitch(12, ...)'.
    `assumed` names arguments the guest never stated (shown as orange chips), so the question says so."""
    a = call["arguments"]
    check_in, check_out = date.fromisoformat(a["check_in"]), date.fromisoformat(a["check_out"])
    nights = (check_out - check_in).days
    party = _plural(a["adults"], "adult")
    if a["children"]:
        party += ", " + _plural(a["children"], "child", "children")
    if a["dogs"]:
        party += " and " + _plural(a["dogs"], "dog")
    if a["vehicle"] == "tent":
        kit = "a tent"
    elif "vehicle_length_m" in assumed:
        kit = f"a {a['vehicle']} of about {a['vehicle_length_m']:g} m (I assumed the length)"
    else:
        kit = f"a {a['vehicle_length_m']:g} m {a['vehicle']}"
    question = (f"Hold Pitch {pitch['id']} ({pitch['area']}, {pitch['surface']}) for {_plural(nights, 'night')}, "
                f"{check_in.strftime('%a')} {check_in.day} {MONTHS[check_in.month - 1]} to "
                f"{check_out.strftime('%a')} {check_out.day} {MONTHS[check_out.month - 1]} {check_out.year}, "
                f"for {party} with {kit}{', with hook-up' if a['hookup'] else ''}?")
    total = pitch["price"] * nights
    consequence = (f"The hold lasts {HOLD_HOURS} hours and keeps the pitch for you. Nothing is paid "
                   f"(the stay would cost £{total}), no booking is confirmed and nobody is contacted.")
    return {"question": question, "consequence": consequence}


# --------------------------------------------------------------------------------------------
# Run, check 5 (idempotency), and the log
# --------------------------------------------------------------------------------------------

def log(call, confirmed, result, session, now=None):
    now = now or datetime.now()
    entry = {"t": now.isoformat(timespec="minutes"), "tool": TOOL["name"],
             "args": call.get("arguments") if isinstance(call, dict) else call,
             "confirmed": confirmed, "session": session, "result": result}
    with _LOCK, open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def run(call, confirmed_by, session, now=None):
    """Execute after confirmation, log, and return what actually happened.
    Every check runs again here, because the files may have changed since the hold was proposed."""
    now = now or datetime.now()
    ok, reason = valid(call)
    if not ok:
        result = {"status": "refused", "check": "shape", "reason": reason}
        log(call, True, result, session, now)
        return result
    with _LOCK:
        ok, reason, pitch = check_now(call, session, now)
        if not ok:
            result = {"status": "refused", "check": "permission or precondition", "reason": reason}
        else:
            a = call["arguments"]
            holds = _load_holds()
            existing = next((h for h in _active(holds, now) if h["session"] == session and h["pitch"] == a["pitch"]
                             and h["check_in"] == a["check_in"] and h["check_out"] == a["check_out"]), None)
            if existing:
                result = {"status": "ok", "hold_id": existing["id"], "pitch": existing["pitch"],
                          "check_in": existing["check_in"], "check_out": existing["check_out"],
                          "expires": existing["expires"], "note": "you already hold this; nothing was added"}
            else:
                hold = {"id": "H-%04d" % (len(holds) + 1), "pitch": a["pitch"], "check_in": a["check_in"],
                        "check_out": a["check_out"], "party": {k: a[k] for k in ("adults", "children", "dogs")},
                        "session": session, "confirmed_by": confirmed_by,
                        "created": now.isoformat(timespec="minutes"),
                        "expires": (now + timedelta(hours=HOLD_HOURS)).isoformat(timespec="minutes")}
                holds.append(hold)
                _save_holds(holds)
                result = {"status": "held", "hold_id": hold["id"], "pitch": hold["pitch"],
                          "check_in": hold["check_in"], "check_out": hold["check_out"], "expires": hold["expires"],
                          "active_holds": len(_active(holds, now))}
    log(call, True, result, session, now)
    return result


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        good = {"name": "hold_pitch", "arguments": {
            "pitch": 12, "check_in": "2027-08-14", "check_out": "2027-08-16", "adults": 2, "children": 0,
            "dogs": 1, "vehicle": "campervan", "vehicle_length_m": 6.0, "hookup": True}}
        bad = {"name": "hold_pitch", "arguments": dict(good["arguments"], check_out="2027-09-04")}
        assert valid(good)[0] and not valid(bad)[0]
        print("ok: valid hold accepted, 21-night hold refused (%s)" % valid(bad)[1])
