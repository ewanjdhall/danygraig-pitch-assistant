"""app.py - Danygraig booking assistant, Lab 3 prototype.

Run it with:  python app.py   then open http://localhost:8000

IMPLEMENTED: the web server, the chat page, the availability lookup in the
             made-up pitch data, ranking with reasons, chip edits and the
             Book -> Confirm step.
SIMULATED:   the language-model step (model.py) and the booking itself:
             nothing is booked and no payment is taken.
PLANNED:     a real LLM call, the park's real booking system, email confirmation.
"""

import json
import os
import re
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import model

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DANYGRAIG_DATA_DIR", os.path.join(HERE, "data"))
PORT = 8000

SYSTEM_INSTRUCTIONS = (
    "You are the booking assistant for Danygraig Holiday Park. Read the guest's message "
    "and return their pitch requirements as JSON that matches the schema: dates, adults, "
    "children, dogs, vehicle type and length, and whether they need electric hook-up. "
    "Fill in every field."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "check_in": {"type": "string", "format": "date"},
        "check_out": {"type": "string", "format": "date"},
        "adults": {"type": "integer", "minimum": 1},
        "children": {"type": "integer", "minimum": 0},
        "dogs": {"type": "integer", "minimum": 0},
        "vehicle": {"type": "string", "enum": ["tent", "campervan", "motorhome", "caravan"]},
        "vehicle_length_m": {"type": "number"},
        "hookup": {"type": "boolean"},
        "out_of_scope": {"type": ["string", "null"]},
    },
    "required": ["check_in", "check_out", "adults", "children", "dogs",
                 "vehicle", "vehicle_length_m", "hookup", "out_of_scope"],
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NOTE = "Prototype: made-up pitch data, and the language-model step is simulated (model.py)."


# --------------------------------------------------------------------------
# Data source: made-up pitches and bookings
# --------------------------------------------------------------------------

class DataUnavailable(Exception):
    pass


def load_data():
    try:
        with open(os.path.join(DATA_DIR, "pitches.json"), encoding="utf-8") as f:
            pitches = json.load(f)["pitches"]
        with open(os.path.join(DATA_DIR, "bookings.json"), encoding="utf-8") as f:
            bookings = json.load(f)["bookings"]
    except (OSError, ValueError, KeyError) as error:
        raise DataUnavailable(str(error))
    return pitches, bookings


# --------------------------------------------------------------------------
# Wording helpers
# --------------------------------------------------------------------------

def day_text(d):
    return f"{d.day} {MONTHS[d.month - 1]}"


def range_text(check_in, check_out):
    if check_in.month == check_out.month:
        return f"{check_in.day}–{check_out.day} {MONTHS[check_in.month - 1]}"
    return f"{day_text(check_in)} – {day_text(check_out)}"


def plural(n, word, plural_word=None):
    return f"{n} {word if n == 1 else (plural_word or word + 's')}"


def dates_of(req):
    return date.fromisoformat(req["check_in"]), date.fromisoformat(req["check_out"])


def vehicle_text(req):
    if req["vehicle"] == "tent":
        return "tent"
    return f"{req['vehicle']} {req['vehicle_length_m']:g} m"


# --------------------------------------------------------------------------
# Availability lookup and ranking (implemented)
# --------------------------------------------------------------------------

def clash(pitch_id, check_in, check_out, bookings):
    for booking in bookings:
        if booking["pitch"] != pitch_id:
            continue
        booked_in = date.fromisoformat(booking["check_in"])
        booked_out = date.fromisoformat(booking["check_out"])
        if check_in < booked_out and booked_in < check_out:
            return booked_in, booked_out
    return None


def problems(pitch, req, bookings):
    """Why a pitch does not fit these requirements. An empty list means it fits."""
    check_in, check_out = dates_of(req)
    found = []
    if pitch.get("tents_only") and req["vehicle"] != "tent":
        found.append("it's for tents only")
    if req["vehicle"] == "tent" and pitch["surface"] == "hardstanding":
        found.append("it's hardstanding, not for tents")
    if req["vehicle"] != "tent" and req["vehicle_length_m"] > pitch["max_length_m"]:
        found.append(f"it takes vehicles up to {pitch['max_length_m']:g} m")
    if req["hookup"] and not pitch["hookup"]:
        found.append("it has no electric hook-up")
    if req["dogs"] and not pitch["dogs"]:
        found.append("dogs aren't allowed there")
    if req["adults"] + req["children"] > pitch["max_guests"]:
        found.append(f"it takes up to {pitch['max_guests']} people")
    booked = clash(pitch["id"], check_in, check_out, bookings)
    if booked:
        found.append(f"it's booked {range_text(*booked)}")
    return found


def rank_key(pitch, req):
    keep_for_dogs = 1 if (req["dogs"] == 0 and pitch["dogs"]) else 0  # save dog-friendly pitches
    wrong_surface = 0 if (req["vehicle"] == "tent") == (pitch["surface"] == "grass") else 1
    spare = 0 if req["vehicle"] == "tent" else pitch["max_length_m"] - req["vehicle_length_m"]
    return keep_for_dogs, wrong_surface, spare, pitch["price"], pitch["id"]


def find_pitches(req, pitches, bookings):
    fits, near = [], []
    for pitch in pitches:
        reasons_against = problems(pitch, req, bookings)
        if not reasons_against:
            fits.append(pitch)
        elif len(reasons_against) == 1:
            near.append({"pitch": f"Pitch {pitch['id']}", "why_not": reasons_against[0]})
    fits.sort(key=lambda pitch: rank_key(pitch, req))
    return fits, near


def pitch_card(pitch, req):
    check_in, check_out = dates_of(req)
    nights = (check_out - check_in).days
    reasons = []
    if req["vehicle"] == "tent":
        reasons.append("grass pitch for your tent")
    else:
        reasons.append(f"fits your {req['vehicle_length_m']:g} m {req['vehicle']} "
                       f"(takes up to {pitch['max_length_m']:g} m)")
    if req["hookup"]:
        reasons.append("has electric hook-up")
    if req["dogs"]:
        reasons.append("dogs welcome")
    elif pitch["area"] == "Orchard":
        reasons.append("quiet, no-dogs area")
    elif not pitch["dogs"]:
        reasons.append("no-dogs area")
    reasons.append(f"free {range_text(check_in, check_out)} ({plural(nights, 'night')})")
    return {
        "id": pitch["id"],
        "name": f"Pitch {pitch['id']}",
        "title": f"Pitch {pitch['id']} – {pitch['area']} ({pitch['surface']})",
        "reasons": reasons,
        "price": f"£{pitch['price']} a night, £{pitch['price'] * nights} in total",
        "summary": [f"Pitch {pitch['id']}, {pitch['area']} ({pitch['surface']})",
                    f"{range_text(check_in, check_out)} ({plural(nights, 'night')})",
                    party_text(req), vehicle_text(req),
                    f"£{pitch['price'] * nights} in total"],
    }


def party_text(req):
    text = plural(req["adults"], "adult")
    if req["children"]:
        text += ", " + plural(req["children"], "child", "children")
    if req["dogs"]:
        text += ", " + plural(req["dogs"], "dog")
    return text


# --------------------------------------------------------------------------
# What the guest sees: chips ("here's what I understood")
# --------------------------------------------------------------------------

def chips_for(req):
    check_in, check_out = dates_of(req)
    nights = (check_out - check_in).days
    chips = [
        {"field": "dates", "label": f"{range_text(check_in, check_out)} ({plural(nights, 'night')})",
         "hint": "e.g. 14-16 Aug"},
        {"field": "adults", "label": plural(req["adults"], "adult"), "hint": "number of adults"},
    ]
    if req["children"]:
        chips.append({"field": "children", "label": plural(req["children"], "child", "children"),
                      "hint": "number of children"})
    chips += [
        {"field": "vehicle", "label": vehicle_text(req), "hint": "e.g. campervan 6m"},
        {"field": "hookup", "label": "hook-up" if req["hookup"] else "no hook-up",
         "hint": "yes or no"},
        {"field": "dogs", "label": plural(req["dogs"], "dog") if req["dogs"] else "pets: none",
         "hint": "number of dogs"},
    ]
    for chip in chips:
        chip["source"] = "shown"
    return chips


# --------------------------------------------------------------------------
# Chip edits (structured, so no model call is needed)
# --------------------------------------------------------------------------

def read_count(text):
    text = text.strip().lower()
    if re.search(r"\b(?:none|no|zero)\b", text):
        return 0
    found = re.search(r"\d+|one|two|three|four|five|six|seven|eight", text)
    return model.number(found.group(0)) if found else None


def read_yes_no(text):
    text = text.strip().lower()
    if re.search(r"\b(?:no|none|false|not needed|don'?t need)\b", text):
        return False
    if re.search(r"\b(?:yes|y|true|need(?:ed)?|hook[\s-]?up|power|electric)\b", text):
        return True
    return None


def apply_edits(req, edits):
    req, changes, errors = dict(req), [], []
    for field, text in (edits or {}).items():
        text = str(text)
        if field == "dates":
            dates = model.find_dates(text)
            if dates["kind"] == "range":
                req["check_in"], req["check_out"] = (dates["check_in"].isoformat(),
                                                     dates["check_out"].isoformat())
            elif dates["kind"] == "single" and dates.get("nights"):
                check_in = dates["check_in"]
                req["check_in"] = check_in.isoformat()
                req["check_out"] = date.fromordinal(check_in.toordinal() + dates["nights"]).isoformat()
            else:
                errors.append("I couldn't read those dates. Try something like 14-16 Aug.")
                continue
            changes.append(f"dates → {range_text(*dates_of(req))}")
        elif field in ("adults", "children", "dogs"):
            value = read_count(text)
            if value is None:
                errors.append(f"I couldn't read a number for {field}.")
                continue
            req[field] = value
            changes.append(f"{field} → {value}")
        elif field == "vehicle":
            vehicle, length = model.find_vehicle(text), model.find_length(text)
            if not vehicle and not length:
                errors.append("I couldn't read that vehicle. Try something like campervan 6m.")
                continue
            if vehicle and vehicle[0] != req["vehicle"]:
                req["vehicle"] = vehicle[0]
                req["vehicle_length_m"] = model.TYPICAL_LENGTH_M[vehicle[0]]
            if length:
                req["vehicle_length_m"] = length[0]
            changes.append(f"vehicle → {vehicle_text(req)}")
        elif field == "hookup":
            value = read_yes_no(text)
            if value is None:
                errors.append("Do you need hook-up? Answer yes or no.")
                continue
            req["hookup"] = value
            changes.append("hook-up → " + ("yes" if value else "no"))
    return req, changes, errors


# --------------------------------------------------------------------------
# One turn of the conversation
# --------------------------------------------------------------------------

def build_parts(message, previous):
    parts = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]
    if previous:
        parts.append({"role": "system", "content": "Requirements so far: " + json.dumps(previous)})
    if message.strip():
        parts.append({"role": "user", "content": message})
    return parts


def respond(reply, state, trace, **extra):
    data = {"version": "v1", "reply": reply, "chips": [], "questions": [],
            "recommendation": None, "alternatives": [], "near_misses": [],
            "actions": [], "note": NOTE, "state": state, "trace": trace}
    data.update(extra)
    return data


def turn(message, state=None, edits=None):
    """Receive the guest's message (or chip edits) and return what the page should show."""
    state = state or {}
    previous = state.get("requirements")
    parts = build_parts(message, previous)
    trace = {"parts": parts}

    try:
        pitches, bookings = load_data()
    except DataUnavailable as error:
        trace["data_error"] = str(error)
        return respond("I can't check which pitches are free right now, so I won't suggest one. "
                       "Please try again later or call reception.", state, trace,
                       actions=["try_again"])

    if message.strip():
        req = model.call_json(parts, SCHEMA)  # SIMULATED language-model step
        trace["model_output"] = dict(req)
    elif previous:
        req = dict(previous)
    else:
        return respond("Tell me who's coming, when, and what you're bringing.", state, trace)

    if req.get("out_of_scope") and not edits:
        return respond("Sorry, I can only help you choose a touring or tent pitch at Danygraig: "
                       "your dates, who's coming, your vehicle, hook-up and dogs. For "
                       f"{req['out_of_scope']}, please contact reception.", state, trace,
                       chips=chips_for(previous) if previous else [], actions=["rephrase"])
    req.pop("out_of_scope", None)

    changes, errors = [], []
    if edits:
        req, changes, errors = apply_edits(req, edits)
        trace["edits"] = {"asked": edits, "applied": changes, "errors": errors}

    fits, near = find_pitches(req, pitches, bookings)
    trace["lookup"] = {"pitches_checked": len(pitches),
                       "fit_in_rank_order": [f"Pitch {p['id']}" for p in fits],
                       "near_misses": near}

    lines = []
    if changes:
        lines.append("Updated: " + ", ".join(changes) + ".")
    lines += errors
    last = state.get("last_pitch")
    if last and fits and fits[0]["id"] != last:
        reason = next((problems(p, req, bookings) for p in pitches if p["id"] == last), [])
        if reason:
            lines.append(f"Pitch {last} doesn't work any more ({reason[0]}), so here's another.")
    lines.append("Here's what I understood. Tap anything that's wrong.")
    new_state = {"requirements": req, "last_pitch": fits[0]["id"] if fits else None}

    if not fits:
        lines.append("No free pitch fits all of that for those dates.")
        return respond(" ".join(lines), new_state, trace, chips=chips_for(req),
                       near_misses=near[:3], actions=["change"])

    return respond(" ".join(lines), new_state, trace, chips=chips_for(req),
                   recommendation=pitch_card(fits[0], req),
                   alternatives=[pitch_card(p, req) for p in fits[1:3]],
                   actions=["book", "change", "other_options"])


# --------------------------------------------------------------------------
# Web server
# --------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        else:
            self._send(404, "Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/turn":
            self._send(404, "Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            self._send(400, json.dumps({"reply": "That request wasn't valid JSON."}),
                       "application/json")
            return
        try:
            data = turn(body.get("message", ""), body.get("state"), body.get("edits"))
            self._send(200, json.dumps(data), "application/json")
        except Exception as error:  # say so honestly rather than guess
            self._send(500, json.dumps({"reply": "Something went wrong on my side, so I won't "
                                                 "guess. Please try again.",
                                        "error": repr(error)}), "application/json")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Danygraig booking assistant (Lab 3 prototype) at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
