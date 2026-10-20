"""app.py - Danygraig booking assistant, Lab 3 prototype.

Run it with:  python app.py   then open http://localhost:8000
The original version (before the Phase 4 changes) still runs with:  python app.py --v1

IMPLEMENTED: the web server, the chat page, the validation step (v2), the
             availability lookup in the made-up pitch data, ranking with
             reasons, chip edits and the Book -> Confirm step.
SIMULATED:   the language-model step (model.py) and the booking itself:
             nothing is booked and no payment is taken.
PLANNED:     a real LLM call, the park's real booking system, email confirmation.
"""

import copy
import json
import os
import re
import sys
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import model

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DANYGRAIG_DATA_DIR", os.path.join(HERE, "data"))
PORT = 8000
VERSION = "v2"  # "v1" = the path as first built and tested; "v2" = after the Phase 4 changes

SYSTEM_INSTRUCTIONS = {
    "v1": ("You are the booking assistant for Danygraig Holiday Park. Read the guest's message "
           "and return their pitch requirements as JSON that matches the schema: dates, adults, "
           "children, dogs, vehicle type and length, and whether they need electric hook-up. "
           "Fill in every field."),
    "v2": ("You are the booking assistant for Danygraig Holiday Park. Read the guest's message "
           "and return their pitch requirements as JSON that matches the schema. For every field "
           "give the value, where it came from (stated by the guest, assumed by you, vague, or "
           "missing) and the guest's own words as evidence. Never guess dates or how many people "
           "are coming: mark them vague or missing. If a name could be a person or a pet, list "
           "it in unclear_names instead of counting it."),
}

SCHEMA_V1 = {
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


def _field(value_schema):
    return {"type": "object",
            "properties": {"value": value_schema,
                           "source": {"enum": ["stated", "assumed", "vague", "missing", "edited"]},
                           "evidence": {"type": "string"}},
            "required": ["value", "source", "evidence"]}


SCHEMA_V2 = {
    "type": "object",
    "properties": {
        "check_in": _field({"type": ["string", "null"], "format": "date"}),
        "check_out": _field({"type": ["string", "null"], "format": "date"}),
        "adults": _field({"type": ["integer", "null"]}),
        "children": _field({"type": ["integer", "null"]}),
        "dogs": _field({"type": ["integer", "null"]}),
        "vehicle": _field({"type": ["string", "null"],
                           "enum": ["tent", "campervan", "motorhome", "caravan", None]}),
        "vehicle_length_m": _field({"type": ["number", "null"]}),
        "hookup": _field({"type": ["boolean", "null"]}),
        "unclear_names": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "evidence": {"type": "string"}}}},
        "out_of_scope": {"type": ["string", "null"]},
    },
    "required": ["check_in", "check_out", "adults", "children", "dogs", "vehicle",
                 "vehicle_length_m", "hookup", "unclear_names", "out_of_scope"],
}

SCHEMAS = {"v1": SCHEMA_V1, "v2": SCHEMA_V2}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NOTE = "Prototype: made-up pitch data, and the language-model step is simulated (model.py)."
MAX_NIGHTS = 14


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
# Requirements: v1 keeps plain values, v2 keeps value + source + evidence
# --------------------------------------------------------------------------

def values_of(req):
    """Plain values, whichever version produced the requirements."""
    return {name: (req[name]["value"] if isinstance(req.get(name), dict) else req.get(name))
            for name in model.FIELDS}


def source_of(req, name):
    item = req.get(name)
    return item.get("source", "stated") if isinstance(item, dict) else "shown"


def evidence_of(req, name):
    item = req.get(name)
    return item.get("evidence", "") if isinstance(item, dict) else ""


def set_value(req, name, value, version):
    if version == "v2":
        req[name] = {"value": value, "source": "edited", "evidence": "changed by you"}
    else:
        req[name] = value


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


def dates_of(values):
    return date.fromisoformat(values["check_in"]), date.fromisoformat(values["check_out"])


def vehicle_text(values, assumed_length=False):
    if values["vehicle"] == "tent":
        return "tent"
    return f"{values['vehicle']} {'~' if assumed_length else ''}{values['vehicle_length_m']:g} m"


def party_text(values):
    text = plural(values["adults"], "adult")
    if values["children"]:
        text += ", " + plural(values["children"], "child", "children")
    if values["dogs"]:
        text += ", " + plural(values["dogs"], "dog")
    return text


# --------------------------------------------------------------------------
# v2: validation step between the model and the lookup (implemented)
# --------------------------------------------------------------------------

def validate(req):
    """Questions to ask before searching, most important first. Empty list = ready."""
    values, questions = values_of(req), []
    if values["check_in"] is None or values["check_out"] is None:
        evidence = evidence_of(req, "check_in")
        if source_of(req, "check_in") == "vague":
            text = f"Which nights exactly? You said “{evidence}”. (For example: 14–16 Aug)"
        elif values["check_in"]:
            text = f"How many nights from {day_text(date.fromisoformat(values['check_in']))}?"
        else:
            text = "Which dates would you like? (For example: 14–16 Aug)"
        questions.append({"id": "dates", "text": text, "quick_replies": []})
    else:
        check_in, check_out = dates_of(values)
        nights = (check_out - check_in).days
        if (check_in < model.SEASON_START or check_out > model.SEASON_END + timedelta(days=1)
                or not 1 <= nights <= MAX_NIGHTS):
            questions.append({"id": "dates", "quick_replies": [], "text": (
                "The park is open 1 Mar – 31 Oct 2027 in this prototype, for stays of up to "
                f"{MAX_NIGHTS} nights. Which dates would you like?")})
    for item in req.get("unclear_names", []):
        name = item["name"]
        questions.append({"id": f"name:{name}", "text": f"Is {name} coming as a guest or a pet?",
                          "quick_replies": [f"{name} is a guest", f"{name} is a pet"]})
    if values["adults"] is None:
        questions.append({"id": "adults", "text": "How many people are coming?", "quick_replies": []})
    if values["vehicle"] is None:
        questions.append({"id": "vehicle",
                          "text": "What are you bringing: a tent, campervan, motorhome or caravan?",
                          "quick_replies": ["Tent", "Campervan", "Motorhome", "Caravan"]})
    return questions


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


def problems(pitch, values, bookings):
    """Why a pitch does not fit these requirements. An empty list means it fits."""
    check_in, check_out = dates_of(values)
    found = []
    if pitch.get("tents_only") and values["vehicle"] != "tent":
        found.append("it's for tents only")
    if values["vehicle"] == "tent" and pitch["surface"] == "hardstanding":
        found.append("it's hardstanding, not for tents")
    if values["vehicle"] != "tent" and values["vehicle_length_m"] > pitch["max_length_m"]:
        found.append(f"it takes vehicles up to {pitch['max_length_m']:g} m")
    if values["hookup"] and not pitch["hookup"]:
        found.append("it has no electric hook-up")
    if values["dogs"] and not pitch["dogs"]:
        found.append("dogs aren't allowed there")
    if values["adults"] + values["children"] > pitch["max_guests"]:
        found.append(f"it takes up to {pitch['max_guests']} people")
    booked = clash(pitch["id"], check_in, check_out, bookings)
    if booked:
        found.append(f"it's booked {range_text(*booked)}")
    return found


def rank_key(pitch, values):
    keep_for_dogs = 1 if (values["dogs"] == 0 and pitch["dogs"]) else 0  # save dog-friendly pitches
    wrong_surface = 0 if (values["vehicle"] == "tent") == (pitch["surface"] == "grass") else 1
    spare = 0 if values["vehicle"] == "tent" else pitch["max_length_m"] - values["vehicle_length_m"]
    return keep_for_dogs, wrong_surface, spare, pitch["price"], pitch["id"]


def find_pitches(values, pitches, bookings):
    fits, near = [], []
    for pitch in pitches:
        reasons_against = problems(pitch, values, bookings)
        if not reasons_against:
            fits.append(pitch)
        elif len(reasons_against) == 1:
            near.append({"pitch": f"Pitch {pitch['id']}", "why_not": reasons_against[0]})
    fits.sort(key=lambda pitch: rank_key(pitch, values))
    return fits, near


def pitch_card(pitch, values, assumed_length=False):
    check_in, check_out = dates_of(values)
    nights = (check_out - check_in).days
    reasons = []
    if values["vehicle"] == "tent":
        reasons.append("grass pitch for your tent")
    elif assumed_length:
        reasons.append(f"takes a {values['vehicle']} up to {pitch['max_length_m']:g} m "
                       f"(I've assumed yours is about {values['vehicle_length_m']:g} m)")
    else:
        reasons.append(f"fits your {values['vehicle_length_m']:g} m {values['vehicle']} "
                       f"(takes up to {pitch['max_length_m']:g} m)")
    if values["hookup"]:
        reasons.append("has electric hook-up")
    if values["dogs"]:
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
                    party_text(values), vehicle_text(values, assumed_length),
                    f"£{pitch['price'] * nights} in total"],
    }


# --------------------------------------------------------------------------
# What the guest sees: chips ("here's what I understood")
# --------------------------------------------------------------------------

def _combined(*sources):
    for source in ("missing", "vague", "edited", "assumed"):
        if source in sources:
            return source
    return sources[0]


def chips_for(req, version):
    values, chips = values_of(req), []

    def add(field, label, source, evidence, hint):
        chips.append({"field": field, "label": label, "source": source,
                      "evidence": evidence, "hint": hint})

    if values["check_in"] and values["check_out"]:
        check_in, check_out = dates_of(values)
        nights = (check_out - check_in).days
        add("dates", f"{range_text(check_in, check_out)} ({plural(nights, 'night')})",
            _combined(source_of(req, "check_in"), source_of(req, "check_out")),
            evidence_of(req, "check_in"), "e.g. 14-16 Aug")
    elif source_of(req, "check_in") == "vague":
        add("dates", f"dates: {evidence_of(req, 'check_in')}?", "vague",
            evidence_of(req, "check_in"), "e.g. 14-16 Aug")
    elif values["check_in"]:
        add("dates", f"from {day_text(date.fromisoformat(values['check_in']))}: how many nights?",
            "missing", "", "e.g. 14-16 Aug")
    else:
        add("dates", "dates?", "missing", "", "e.g. 14-16 Aug")

    if values["adults"] is not None:
        add("adults", plural(values["adults"], "adult"), source_of(req, "adults"),
            evidence_of(req, "adults"), "number of adults")
    else:
        add("adults", "how many people?", "missing", "", "number of adults")
    if values["children"]:
        add("children", plural(values["children"], "child", "children"), source_of(req, "children"),
            evidence_of(req, "children"), "number of children")
    unclear = req.get("unclear_names", []) if isinstance(req, dict) else []
    for item in unclear:
        add(f"name:{item['name']}", f"{item['name']}: guest or pet?", "unclear",
            item["evidence"], "guest or pet")

    if values["vehicle"]:
        length_source = source_of(req, "vehicle_length_m")
        assumed = version == "v2" and length_source == "assumed"
        add("vehicle", vehicle_text(values, assumed),
            _combined(source_of(req, "vehicle"), length_source),
            evidence_of(req, "vehicle_length_m") if assumed else evidence_of(req, "vehicle"),
            "e.g. campervan 6m")
    else:
        add("vehicle", "vehicle?", "missing", "", "tent, campervan, motorhome or caravan")
    if values["hookup"] is not None:
        add("hookup", "hook-up" if values["hookup"] else "no hook-up", source_of(req, "hookup"),
            evidence_of(req, "hookup"), "yes or no")
    if not unclear and values["dogs"] is not None:
        add("dogs", plural(values["dogs"], "dog") if values["dogs"] else "pets: none",
            source_of(req, "dogs"), evidence_of(req, "dogs"), "number of dogs")
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


def apply_edits(req, edits, version):
    req, changes, errors = copy.deepcopy(req), [], []
    for field, text in (edits or {}).items():
        text, values = str(text), values_of(req)
        if field == "dates":
            dates = model.find_dates(text)
            if dates["kind"] == "range":
                check_in, check_out = dates["check_in"], dates["check_out"]
            elif dates["kind"] == "single" and dates.get("nights"):
                check_in = dates["check_in"]
                check_out = check_in + timedelta(days=dates["nights"])
            else:
                errors.append("I couldn't read those dates. Try something like 14-16 Aug.")
                continue
            set_value(req, "check_in", check_in.isoformat(), version)
            set_value(req, "check_out", check_out.isoformat(), version)
            changes.append(f"dates → {range_text(check_in, check_out)}")
        elif field in ("adults", "children", "dogs"):
            value = read_count(text)
            if value is None:
                errors.append(f"I couldn't read a number for {field}.")
                continue
            set_value(req, field, value, version)
            changes.append(f"{field} → {value}")
        elif field == "vehicle":
            vehicle, length = model.find_vehicle(text), model.find_length(text)
            if not vehicle and not length:
                errors.append("I couldn't read that vehicle. Try something like campervan 6m.")
                continue
            if vehicle and vehicle[0] != values["vehicle"]:
                set_value(req, "vehicle", vehicle[0], version)
                set_value(req, "vehicle_length_m", model.TYPICAL_LENGTH_M[vehicle[0]], version)
                if version == "v2" and vehicle[0] != "tent" and not length:
                    req["vehicle_length_m"]["source"] = "assumed"
                    req["vehicle_length_m"]["evidence"] = "typical length for that vehicle"
            if length:
                set_value(req, "vehicle_length_m", length[0], version)
            changes.append(f"vehicle → {vehicle_text(values_of(req))}")
        elif field == "hookup":
            value = read_yes_no(text)
            if value is None:
                errors.append("Do you need hook-up? Answer yes or no.")
                continue
            set_value(req, "hookup", value, version)
            changes.append("hook-up → " + ("yes" if value else "no"))
        elif field.startswith("name:") and version == "v2":
            name = field[5:]
            kind = "pet" if re.search(r"\b(?:pet|dog|puppy)\b", text, re.I) else (
                "guest" if re.search(r"\b(?:guest|person|adult|human)\b", text, re.I) else None)
            if not kind:
                errors.append(f"Is {name} a guest or a pet?")
                continue
            req["unclear_names"] = [n for n in req.get("unclear_names", []) if n["name"] != name]
            target = "dogs" if kind == "pet" else "adults"
            set_value(req, target, (values[target] or 0) + 1, version)
            changes.append(f"{name} → {kind}")
    return req, changes, errors


# --------------------------------------------------------------------------
# One turn of the conversation
# --------------------------------------------------------------------------

def build_parts(message, previous, version):
    parts = [{"role": "system", "content": SYSTEM_INSTRUCTIONS[version]}]
    if previous:
        parts.append({"role": "system", "content": "Requirements so far: " + json.dumps(previous)})
    if message.strip():
        parts.append({"role": "user", "content": message})
    return parts


def respond(version, reply, state, trace, **extra):
    data = {"version": version, "reply": reply, "chips": [], "questions": [],
            "recommendation": None, "alternatives": [], "near_misses": [],
            "actions": [], "note": NOTE, "state": state, "trace": trace}
    data.update(extra)
    return data


def turn(message, state=None, edits=None, version=None):
    """Receive the guest's message (or chip edits) and return what the page should show."""
    version = version or VERSION
    state = state or {}
    previous = state.get("requirements")
    parts = build_parts(message, previous, version)
    trace = {"version": version, "parts": parts}

    try:
        pitches, bookings = load_data()
    except DataUnavailable as error:
        trace["data_error"] = str(error)
        return respond(version, "I can't check which pitches are free right now, so I won't "
                       "suggest one. Please try again later or call reception.", state, trace,
                       actions=["try_again"])

    if message.strip():
        req = model.call_json(parts, SCHEMAS[version])  # SIMULATED language-model step
        trace["model_output"] = copy.deepcopy(req)
    elif previous:
        req = copy.deepcopy(previous)
    else:
        return respond(version, "Tell me who's coming, when, and what you're bringing.", state, trace)

    if req.get("out_of_scope") and not edits:
        return respond(version, "Sorry, I can only help you choose a touring or tent pitch at "
                       "Danygraig: your dates, who's coming, your vehicle, hook-up and dogs. For "
                       f"{req['out_of_scope']}, please contact reception.", state, trace,
                       chips=chips_for(previous, version) if previous else [],
                       actions=["rephrase"])
    req.pop("out_of_scope", None)

    lines = []
    if version == "v2" and previous:
        still = {item["name"] for item in req.get("unclear_names", [])}
        before, after = values_of(previous), values_of(req)
        for item in previous.get("unclear_names", []):
            if item["name"] not in still:
                kind = "a dog" if (after["dogs"] or 0) > (before["dogs"] or 0) else "a guest"
                lines.append(f"Thanks, {item['name']} is down as {kind}.")
    changes, errors = [], []
    if edits:
        req, changes, errors = apply_edits(req, edits, version)
        trace["edits"] = {"asked": edits, "applied": changes, "errors": errors}
        if changes:
            lines.append("Updated: " + ", ".join(changes) + ".")
        lines += errors

    if version == "v2":
        questions = validate(req)
        trace["validation"] = [q["text"] for q in questions]
        if questions:
            lines.append("Here's what I understood so far. Before I look for a pitch:")
            return respond(version, " ".join(lines),
                           {"requirements": req, "last_pitch": state.get("last_pitch")}, trace,
                           chips=chips_for(req, version), questions=questions[:2],
                           actions=["answer", "change"])

    values = values_of(req)
    fits, near = find_pitches(values, pitches, bookings)
    trace["lookup"] = {"pitches_checked": len(pitches),
                       "fit_in_rank_order": [f"Pitch {p['id']}" for p in fits],
                       "near_misses": near}

    last = state.get("last_pitch")
    if last and fits and fits[0]["id"] != last:
        reason = next((problems(p, values, bookings) for p in pitches if p["id"] == last), [])
        if reason:
            lines.append(f"Pitch {last} doesn't work any more ({reason[0]}), so here's another.")
    lines.append("Here's what I understood. Tap anything that's wrong.")
    chips = chips_for(req, version)
    if version == "v2" and any(chip["source"] == "assumed" for chip in chips):
        lines.append("I've assumed the orange ones.")
    new_state = {"requirements": req, "last_pitch": fits[0]["id"] if fits else None}

    if not fits:
        lines.append("No free pitch fits all of that for those dates.")
        return respond(version, " ".join(lines), new_state, trace, chips=chips,
                       near_misses=near[:3], actions=["change"])

    assumed_length = version == "v2" and source_of(req, "vehicle_length_m") == "assumed"
    return respond(version, " ".join(lines), new_state, trace, chips=chips,
                   recommendation=pitch_card(fits[0], values, assumed_length),
                   alternatives=[pitch_card(p, values, assumed_length) for p in fits[1:3]],
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
    global VERSION
    if "--v1" in sys.argv[1:]:
        VERSION = "v1"
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Danygraig booking assistant (Lab 3 prototype, {VERSION}) at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
