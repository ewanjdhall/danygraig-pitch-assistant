"""model.py - the language-model step of the Danygraig booking assistant (Lab 3).

PLANNED: a large language model reads the conversation (`parts`) and returns
the guest's booking requirements as JSON that matches SCHEMA (structured
output).

SIMULATED HERE: a small rule-based extractor with the same interface,
`call_json(parts, schema)`. It needs no API key or network and always gives
the same answer for the same input, so Test A and Test B can be replayed
exactly. It behaves the way a model would under each schema:

* v1 schema: every field is required and must hold a value, so gaps are filled
  with plausible guesses (vague dates become a definite stay, an unknown name
  becomes another adult, a missing vehicle length becomes a typical one), and
  nothing in the output says which values were guessed.
* v2 schema: every field carries value + source (stated / assumed / vague /
  missing) + evidence (the guest's words), and names that could be a person or
  a pet are listed in unclear_names instead of being counted.
* v3 schema (Lab 4): the v2 schema plus a `question` field. When the guest asks
  about the park instead of describing their stay, the question is copied there
  and the requirements are returned unchanged, so the app can answer it from the
  guest information (retrieve.py) without touching the booking.

Lab 4 also adds answer_from_passages(), the SIMULATED answer step for those
questions: it quotes the chosen passage word for word instead of writing an
answer. PLANNED: a real model writes a short answer from the quoted passages.
"""

import copy
import json
import re
from datetime import date, timedelta

SIMULATED = True  # shown in the interface so nobody mistakes this for a real model

SEASON_YEAR = 2027  # the made-up data only covers the 2027 season
SEASON_START = date(2027, 3, 1)
SEASON_END = date(2027, 10, 31)
DEFAULT_NIGHTS = 2
TYPICAL_LENGTH_M = {"campervan": 6.0, "motorhome": 7.5, "caravan": 7.0, "tent": 0.0}
FIELDS = ["check_in", "check_out", "adults", "children", "dogs",
          "vehicle", "vehicle_length_m", "hookup"]

# --------------------------------------------------------------------------
# Small parsing helpers (also used by app.py to read chip edits)
# --------------------------------------------------------------------------

_MONTH = (r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|"
          r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b")
_DAY = r"(\d{1,2})(?:st|nd|rd|th)?"
_DASH = r"\s*(?:-|–|—|to|until|till)\s*"
_NUM = r"(\d+|an?|one|two|three|four|five|six|seven|eight|a couple of)"
_NUM_WORDS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4,
              "five": 5, "six": 6, "seven": 7, "eight": 8, "a couple of": 2}
_MONTH_NUMBERS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                  "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
_WHEN_DAY = {"early": 3, "start of": 1, "beginning of": 1, "mid": 15,
             "middle of": 15, "late": 25, "end of": 25}


def number(token):
    """'two' -> 2, '3' -> 3, 'a' -> 1."""
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return _NUM_WORDS.get(token)


def _month(token):
    return _MONTH_NUMBERS[token.lower()[:3]]


def _day(day, month):
    try:
        return date(SEASON_YEAR, month, int(day))
    except ValueError:
        return None


def find_dates(text):
    """Return what the text says about the stay dates.

    kind is one of: range (both dates), single (arrival date only),
    vague (a month or a phrase like 'next weekend'), invalid, none.
    """
    nights_match = re.search(r"\b" + _NUM + r"\s+nights?\b", text, re.I)
    nights = number(nights_match.group(1)) if nights_match else None

    two_months = re.search(_DAY + r"\s+(?:of\s+)?" + _MONTH + _DASH + _DAY +
                           r"\s+(?:of\s+)?" + _MONTH, text, re.I)
    if two_months:
        start = _day(two_months.group(1), _month(two_months.group(2)))
        end = _day(two_months.group(3), _month(two_months.group(4)))
        if start and end and end > start:
            return {"kind": "range", "check_in": start, "check_out": end,
                    "evidence": two_months.group(0)}
        return {"kind": "invalid", "evidence": two_months.group(0)}

    one_month = re.search(_DAY + _DASH + _DAY + r"\s+(?:of\s+)?" + _MONTH, text, re.I)
    if one_month:
        month = _month(one_month.group(3))
        start, end = _day(one_month.group(1), month), _day(one_month.group(2), month)
        if start and end and end > start:
            return {"kind": "range", "check_in": start, "check_out": end,
                    "evidence": one_month.group(0)}
        return {"kind": "invalid", "evidence": one_month.group(0)}

    single = (re.search(_DAY + r"\s+(?:of\s+)?" + _MONTH, text, re.I) or
              re.search(r"\b" + _MONTH + r"\s+" + _DAY + r"\b", text, re.I))
    if single:
        groups = single.groups()
        day, month = (groups[0], groups[1]) if groups[0].isdigit() else (groups[1], groups[0])
        start = _day(day, _month(month))
        if not start:
            return {"kind": "invalid", "evidence": single.group(0)}
        evidence = single.group(0) + (f", {nights_match.group(0)}" if nights_match else "")
        return {"kind": "single", "check_in": start, "nights": nights, "evidence": evidence}

    # A month on its own ("mid August"). 'may' only counts after in/early/mid/late.
    vague = re.search(r"\b(early|mid|middle of|late|end of|start of|beginning of|"
                      r"sometime in|some time in|in)?\s*-?\s*" + _MONTH, text, re.I)
    if vague and (vague.group(2).lower() != "may" or vague.group(1)):
        when = (vague.group(1) or "").lower()
        return {"kind": "vague", "month": _month(vague.group(2)), "when": when,
                "nights": nights, "evidence": vague.group(0).strip()}
    phrase = re.search(r"\b(?:next|this|a)\s+(?:weekend|week)\b|\bbank holiday\b|"
                       r"\bhalf[- ]term\b|\bsummer\b|\beaster\b", text, re.I)
    if phrase:
        return {"kind": "vague", "month": None, "when": "", "nights": nights,
                "evidence": phrase.group(0)}
    if nights:
        return {"kind": "nights_only", "nights": nights, "evidence": nights_match.group(0)}
    return {"kind": "none"}


def find_length(text):
    """'6m', '7.5 metres', '20ft' -> metres, rounded to 0.1 m."""
    metres = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:m|mtrs?|metres?|meters?)\b", text, re.I)
    if metres:
        return round(float(metres.group(1)), 1), metres.group(0)
    feet = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:ft|foot|feet)\b", text, re.I)
    if feet:
        return round(float(feet.group(1)) * 0.3048, 1), feet.group(0)
    return None


def find_vehicle(text):
    for vehicle, pattern in (("motorhome", r"\bmotor\s*-?\s*home\b|\brv\b"),
                             ("campervan", r"\bcamper\s*-?\s*van\b|\bcamper\b|\bvan\b|\bvw\b"),
                             ("caravan", r"\bcaravan\b|\btourer\b"),
                             ("tent", r"\btent\b")):
        found = re.search(pattern, text, re.I)
        if found:
            return vehicle, found.group(0)
    return None


def find_hookup(text):
    no = re.search(r"\b(?:no|don'?t need|without)\s+(?:a\s+)?(?:hook[\s-]?up|power|"
                   r"electric(?:ity|s)?|ehu)\b", text, re.I)
    if no:
        return False, no.group(0)
    yes = re.search(r"\bhook[\s-]?up\b|\behu\b|\belectric(?:ity|s)?\b|\bpower\b|\bmains\b",
                    text, re.I)
    if yes:
        return True, yes.group(0)
    return None


_NOT_NAMES = {
    "i", "me", "my", "our", "the", "a", "an", "we", "us", "kids", "children", "child",
    "dog", "dogs", "pet", "pets", "puppy", "hook", "hookup", "power", "electric", "ehu",
    "campervan", "camper", "van", "motorhome", "caravan", "tent", "awning", "car", "bike",
    "bikes", "trailer", "partner", "wife", "husband", "friend", "friends", "family",
    "mum", "dad", "baby", "grandma", "grandad", "two", "three", "four", "five", "six",
    "jan", "january", "feb", "february", "mar", "march", "apr", "april", "may", "jun",
    "june", "jul", "july", "aug", "august", "sep", "sept", "september", "oct",
    "october", "nov", "november", "dec", "december", "hi", "thanks", "please",
}
_PET_WORDS = r"(?:dog|pet|puppy|pup|spaniel|labrador|lab|terrier|collie|cockapoo)"
_GUEST_WORDS = r"(?:guest|person|human|adult|grown[- ]up|friend|sister|brother|mum|dad|partner|aunt|uncle|nan|gran)"
_CHILD_WORDS = r"(?:child|kid|son|daughter|baby|toddler)"


def find_names(text):
    """Capitalised names after 'plus', 'and', 'with' or '+', e.g. 'two of us plus Bella'."""
    names = []
    for found in re.finditer(r"(?:\b(?i:plus|and|with)|&|\+)\s+([A-Z][a-z]+)\b", text):
        name = found.group(1)
        if name.lower() not in _NOT_NAMES and name not in [n for n, _ in names]:
            names.append((name, found.group(0)))
    return names


def classify_name(name, text):
    """Does the text say whether `name` is a pet, a guest or a child?"""
    n = re.escape(name)
    pet = (rf"\b{n}(?:'s|\s+is)\s+(?:coming\s+as\s+)?(?:our|my|a|the)?\s*{_PET_WORDS}\b|"
           rf"\b{n}\s+(?:the|our|my)\s+{_PET_WORDS}\b|\b{n}\s*\({_PET_WORDS}\)|"
           rf"\b(?:our|my|the)\s+{_PET_WORDS}\s*,?\s+{n}\b")
    guest = (rf"\b{n}(?:'s|\s+is)\s+(?:coming\s+as\s+)?(?:a|an|our|my)?\s*{_GUEST_WORDS}\b|"
             rf"\b{n}\s*\((?:adult|guest|friend)\)")
    child = rf"\b{n}(?:'s|\s+is)\s+(?:our|my|a)?\s*{_CHILD_WORDS}\b"
    for kind, pattern in (("pet", pet), ("child", child), ("guest", guest)):
        found = re.search(pattern, text, re.I)
        if found:
            return kind, found.group(0)
    return None


def find_party(text):
    """Adults and children, e.g. '2 adults', 'two of us', 'me and my partner'."""
    out = {}
    adults = re.search(r"\b" + _NUM + r"\s+(?:adults?|grown[- ]ups?)\b", text, re.I)
    if adults:
        out["adults"] = (number(adults.group(1)), adults.group(0))
    else:
        of_us = re.search(r"\b" + _NUM + r"\s+of\s+us\b", text, re.I)
        couple = re.search(r"\bme and my \w+|\bmy \w+ and (?:i|me)\b|\bthe two of us\b", text, re.I)
        alone = re.search(r"\b(?:just me|only me|on my own|by myself)\b", text, re.I)
        if of_us:
            out["adults"] = (number(of_us.group(1)), of_us.group(0))
        elif couple:
            out["adults"] = (2, couple.group(0))
        elif alone:
            out["adults"] = (1, alone.group(0))
    kids = re.search(r"\b" + _NUM + r"\s+(?:kids?|children|child)\b", text, re.I)
    if kids:
        out["children"] = (number(kids.group(1)), kids.group(0))
    return out


def find_dogs(text):
    """Explicit dog counts: 'no dogs', 'a dog', 'two dogs', 'our dog'."""
    none = re.search(r"\bno\s+(?:dogs?|pets?)\b", text, re.I)
    if none:
        return 0, none.group(0)
    count = re.search(r"\b" + _NUM + r"\s+dogs?\b", text, re.I)
    if count:
        return number(count.group(1)), count.group(0)
    ours = re.search(r"\b(?:our|my|the)\s+(?:dog|puppy|pup|pet)\b", text, re.I)
    if ours:
        return 1, ours.group(0)
    return None


_OUT_OF_SCOPE = [
    (r"\b(?:pub|restaurant|table for|dinner|breakfast|takeaway)\b|\btable\b", "food and drink"),
    (r"\b(?:lodges?|glamping|pods?|cabins?|static caravan|holiday home|cottage)\b",
     "lodges and holiday homes"),
    (r"\b(?:refund|cancel|cancellation|my booking|existing booking)\b",
     "changing or cancelling an existing booking"),
    (r"\b(?:weather|forecast)\b", "the weather"),
    (r"\b(?:taxi|bus|train)\b", "travel to the park"),
]


# v3 (Lab 4): only a request to change or cancel a booking is out of scope; a question about the
# cancellation policy is answered from the guest information instead.
_EXISTING_BOOKING_V3 = (r"\b(?:cancel|change|amend|move)\s+(?:my|our|the|a)\s+booking\b|"
                        r"\brefund\s+(?:my|our|me)\b|\b(?:my|our|existing)\s+booking\b",
                        "changing or cancelling an existing booking")


def find_out_of_scope(text, v3=False):
    rules = _OUT_OF_SCOPE
    if v3:
        rules = [rule for rule in _OUT_OF_SCOPE if "cancel" not in rule[0]] + [_EXISTING_BOOKING_V3]
    for pattern, topic in rules:
        if re.search(pattern, text, re.I):
            return topic
    return None


_QUESTION_START = re.compile(r"^\s*(?:what(?:'s|s)?|when|where|which|who|why|how|can|could|do|does|"
                             r"did|is|are|will|would|may|should|am|have|has)\b", re.I)


def is_question(text):
    return text.strip().endswith("?") or bool(_QUESTION_START.search(text))


def _describes_a_stay(found):
    """Dates, who is coming, a name or a vehicle mean the guest is describing their stay.
    A dog or hook-up on its own does not ("Can I bring my dog?" is a question about the rules)."""
    return bool(found["dates"]["kind"] != "none" or found["party"] or found["names"] or
                found["vehicle"] or found["length"])


# --------------------------------------------------------------------------
# The model call
# --------------------------------------------------------------------------

def _latest_user_text(parts):
    for part in reversed(parts):
        if part.get("role") == "user":
            return part.get("content", "")
    return ""


def _previous_requirements(parts):
    for part in parts:
        content = part.get("content", "")
        if part.get("role") == "system" and content.startswith("Requirements so far:"):
            return json.loads(content.split(":", 1)[1])
    return None


def _first_friday():
    day = SEASON_START
    while day.weekday() != 4:
        day += timedelta(days=1)
    return day


def extract(text, v3=False):
    """Everything the message says, before any guessing."""
    return {
        "dates": find_dates(text),
        "party": find_party(text),
        "names": find_names(text),
        "dogs": find_dogs(text),
        "vehicle": find_vehicle(text),
        "length": find_length(text),
        "hookup": find_hookup(text),
        "out_of_scope": find_out_of_scope(text, v3),
    }


def _fill_every_field(found, previous, text):
    """The schema requires a value for every field, so guess anything missing."""
    out = dict(previous or {})
    dates = found["dates"]
    if dates["kind"] == "range":
        check_in, check_out = dates["check_in"], dates["check_out"]
    elif dates["kind"] == "single":
        check_in = dates["check_in"]
        check_out = check_in + timedelta(days=dates["nights"] or DEFAULT_NIGHTS)
    elif dates["kind"] == "vague":
        if dates["month"]:
            check_in = date(SEASON_YEAR, dates["month"], _WHEN_DAY.get(dates["when"], 15))
        else:
            check_in = _first_friday()
        check_out = check_in + timedelta(days=dates["nights"] or DEFAULT_NIGHTS)
    elif previous and previous.get("check_in"):
        check_in = date.fromisoformat(previous["check_in"])
        check_out = date.fromisoformat(previous["check_out"])
        if dates["kind"] == "nights_only":
            check_out = check_in + timedelta(days=dates["nights"])
    else:
        check_in = _first_friday()
        check_out = check_in + timedelta(days=(dates.get("nights") or DEFAULT_NIGHTS))
    out["check_in"], out["check_out"] = check_in.isoformat(), check_out.isoformat()

    party = found["party"]
    adults = party["adults"][0] if "adults" in party else out.get("adults", 2)
    # Each unknown name is counted as one more person.
    unclear = [name for name, _ in found["names"] if classify_name(name, text) is None]
    pets = [name for name, _ in found["names"] if (classify_name(name, text) or ("",))[0] == "pet"]
    out["adults"] = adults + len(unclear)
    out["children"] = party["children"][0] if "children" in party else out.get("children", 0)
    dogs = found["dogs"][0] if found["dogs"] else out.get("dogs", 0)
    out["dogs"] = max(dogs, len(pets))

    if found["vehicle"]:
        out["vehicle"] = found["vehicle"][0]
    out.setdefault("vehicle", "tent")
    if found["length"]:
        out["vehicle_length_m"] = found["length"][0]
    elif found["vehicle"] or "vehicle_length_m" not in out:
        out["vehicle_length_m"] = TYPICAL_LENGTH_M[out["vehicle"]]
    if found["hookup"]:
        out["hookup"] = found["hookup"][0]
    out.setdefault("hookup", False)
    out["out_of_scope"] = None
    if found["out_of_scope"] and not _has_booking_details(found):
        out["out_of_scope"] = found["out_of_scope"]
    return out


def _has_booking_details(found):
    return bool(found["dates"]["kind"] != "none" or found["party"] or found["names"] or
                found["dogs"] or found["vehicle"] or found["length"] or found["hookup"])


def _field(value, source, evidence=""):
    return {"value": value, "source": source, "evidence": evidence}


def _answer_about_one_name(text):
    """A reply about the only unclear name, e.g. "she's our dog" or just "a pet"."""
    pet = re.search(r"\b(?:she|he|it|they)(?:'s|\s+is|\s+are)\s+(?:our|my|a|the)?\s*" + _PET_WORDS +
                    r"\b|^\s*(?:a\s+|our\s+)?(?:dog|pet)\s*\.?\s*$", text, re.I)
    if pet:
        return "pet", pet.group(0).strip()
    guest = re.search(r"\b(?:she|he|they)(?:'s|\s+is|\s+are)\s+(?:a\s+|an\s+)?" + _GUEST_WORDS +
                      r"\b|^\s*(?:a\s+)?(?:guest|person|adult)\s*\.?\s*$", text, re.I)
    if guest:
        return "guest", guest.group(0).strip()
    return None


def _with_sources(found, previous, text):
    """v2 schema: every field says where its value came from, so nothing has to be guessed."""
    prev = previous or {}
    out = {}
    for name in FIELDS:
        old = prev.get(name)
        out[name] = dict(old) if isinstance(old, dict) else _field(None, "missing")

    # Names that could be a person or a pet: resolve earlier ones, then add new ones.
    pending = [dict(item) for item in prev.get("unclear_names", [])]
    resolved = {"pet": [], "guest": [], "child": []}
    unclear = []
    for item in pending:
        kind = classify_name(item["name"], text)
        if not kind and len(pending) == 1:
            kind = _answer_about_one_name(text)
        if kind:
            resolved[kind[0]].append((item["name"], kind[1]))
        else:
            unclear.append(item)
    for name, evidence in found["names"]:
        if any(item["name"] == name for item in pending):
            continue
        kind = classify_name(name, text)
        if kind:
            resolved[kind[0]].append((name, kind[1]))
        else:
            unclear.append({"name": name, "evidence": evidence})

    # Dates: never turn a vague date into a definite one.
    dates = found["dates"]
    if dates["kind"] == "range":
        out["check_in"] = _field(dates["check_in"].isoformat(), "stated", dates["evidence"])
        out["check_out"] = _field(dates["check_out"].isoformat(), "stated", dates["evidence"])
    elif dates["kind"] == "single":
        out["check_in"] = _field(dates["check_in"].isoformat(), "stated", dates["evidence"])
        if dates["nights"]:
            end = dates["check_in"] + timedelta(days=dates["nights"])
            out["check_out"] = _field(end.isoformat(), "stated", dates["evidence"])
        else:
            out["check_out"] = _field(None, "missing", "no number of nights given")
    elif dates["kind"] in ("vague", "invalid"):
        note = dates["evidence"] if dates["kind"] == "vague" else dates["evidence"] + " (not a date I can use)"
        out["check_in"] = _field(None, "vague", note)
        out["check_out"] = _field(None, "vague", note)
    elif dates["kind"] == "nights_only" and out["check_in"]["value"]:
        end = date.fromisoformat(out["check_in"]["value"]) + timedelta(days=dates["nights"])
        out["check_out"] = _field(end.isoformat(), "stated", dates["evidence"])

    # Who is coming.
    party = found["party"]
    if "adults" in party:
        out["adults"] = _field(party["adults"][0], "stated", party["adults"][1])
    for name, evidence in resolved["guest"]:
        adults = (out["adults"]["value"] or 0) + 1
        out["adults"] = _field(adults, "stated", f"{out['adults']['evidence']} + {evidence}".strip(" +"))
    if "children" in party:
        out["children"] = _field(party["children"][0], "stated", party["children"][1])
    for name, evidence in resolved["child"]:
        out["children"] = _field((out["children"]["value"] or 0) + 1, "stated", evidence)
    if out["children"]["value"] is None:
        out["children"] = _field(0, "assumed", "no children mentioned")

    # Dogs: an explicit count, pets named in this message, or an assumption.
    previous_dogs = out["dogs"]["value"] if out["dogs"]["source"] in ("stated", "edited") else 0
    new_pets = resolved["pet"]
    if found["dogs"] and found["dogs"][0] == 0:
        out["dogs"] = _field(0, "stated", found["dogs"][1])
    elif found["dogs"]:
        count = max(found["dogs"][0], (previous_dogs or 0) + len(new_pets))
        evidence = new_pets[0][1] if new_pets else found["dogs"][1]
        out["dogs"] = _field(count, "stated", evidence)
    elif new_pets:
        out["dogs"] = _field((previous_dogs or 0) + len(new_pets), "stated", new_pets[0][1])
    elif out["dogs"]["source"] not in ("stated", "edited"):
        out["dogs"] = _field(0, "assumed", "no dog mentioned")

    # Vehicle, length and hook-up.
    old_vehicle = out["vehicle"]["value"]
    if found["vehicle"]:
        out["vehicle"] = _field(found["vehicle"][0], "stated", found["vehicle"][1])
    vehicle = out["vehicle"]["value"]
    if found["length"]:
        out["vehicle_length_m"] = _field(found["length"][0], "stated", found["length"][1])
    elif vehicle == "tent":
        out["vehicle_length_m"] = _field(0.0, "stated", "tent")
    elif vehicle and (vehicle != old_vehicle or out["vehicle_length_m"]["value"] is None):
        typical = TYPICAL_LENGTH_M[vehicle]
        out["vehicle_length_m"] = _field(typical, "assumed",
                                         f"no length given; a typical {vehicle} is about {typical:g} m")
    if found["hookup"]:
        out["hookup"] = _field(found["hookup"][0], "stated", found["hookup"][1])
    elif out["hookup"]["value"] is None:
        out["hookup"] = _field(False, "assumed", "hook-up not mentioned")

    out["unclear_names"] = unclear
    answered = any(resolved.values())
    out["out_of_scope"] = None
    if found["out_of_scope"] and not _has_booking_details(found) and not answered:
        out["out_of_scope"] = found["out_of_scope"]
    return out


def _wants_sources(schema):
    """The v2 schema describes each field as an object with value, source and evidence."""
    check_in = schema.get("properties", {}).get("check_in", {})
    return check_in.get("type") == "object"


def _routes_questions(schema):
    """The v3 schema has a `question` field for questions about the park."""
    return "question" in schema.get("properties", {})


def call_json(parts, schema):
    """Stand-in for an LLM structured-output call: returns a dict matching `schema`."""
    text = _latest_user_text(parts).replace("\u2019", "'")  # curly apostrophes
    previous = _previous_requirements(parts)
    v3 = _routes_questions(schema)
    found = extract(text, v3)
    if v3 and is_question(text) and not _describes_a_stay(found) and not found["out_of_scope"]:
        out = copy.deepcopy(previous) if previous else {}
        out["question"] = text.strip()  # requirements unchanged: a question never edits the booking
        out["out_of_scope"] = None
        return out
    if _wants_sources(schema):
        out = _with_sources(found, previous, text)
    else:
        out = _fill_every_field(found, previous, text)
    if v3:
        out["question"] = None
    return out


def answer_from_passages(parts, passage):
    """SIMULATED answer step (Lab 4): quote the chosen passage word for word.

    `parts` is what a real model would receive (instructions, the quoted passages and the question).
    PLANNED: a real model writes a one-sentence answer from those passages, and the app checks that
    the answer's claims appear in the passage before showing it. Quoting avoids adding anything the
    passage does not say."""
    return {"answer": passage["text"], "quoted": True}
