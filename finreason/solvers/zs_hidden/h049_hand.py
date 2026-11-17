"""h049: multi-layer multiplicative tolerance envelope assurance check (enum final)."""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h049"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "single": 1,
}


def _layers(text: str) -> int:
    m = re.search(r"(?:exactly\s+)?(\w+)\s+sequential\s+multiplicative", text)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        if w.isdigit():
            return int(w)
    m = re.search(r"\(1-t\)\^(\d+)", text)
    if m:
        return int(m.group(1))
    raise ValueError("layer count not found")


def _pairs(text: str):
    rx = re.compile(
        r"reported\s+([\w\- ]+?)\s+(" + NUMBER + r")\s+against\s+audited\s+([\w\- ]+?)\s+(" + NUMBER + r")"
    )
    out = []
    for m in rx.finditer(text):
        out.append((m.group(1), F(m.group(2)), F(m.group(4))))
    if not out:
        raise ValueError("no reported/audited pairs")
    return out


def _tolerance(text: str) -> Fraction:
    m = re.search(r"tolerance ratio\s+(" + NUMBER + r")(\s*(?:percent|%))?", text)
    if m is None:
        raise ValueError("tolerance not found")
    t = F(m.group(1))
    if m.group(2):
        t /= 100
    return t


def solve(text: str, q: dict) -> dict:
    t = _tolerance(text)
    n = _layers(text)
    lower_factor = 1 - t
    upper_factor = 1 + t
    lo_mult = lower_factor ** n
    hi_mult = upper_factor ** n

    ok = True
    for _name, rep, aud in _pairs(text):
        lo = rep * lo_mult
        hi = rep * hi_mult
        a, b = min(lo, hi), max(lo, hi)
        if not (a <= aud <= b):  # inclusive envelope
            ok = False

    # Coverage: "Audit coverage X must reach Y" -> X >= Y
    m = re.search(
        r"[Cc]overage\s+(" + NUMBER + r")\s+must\s+(?:reach|be at least|meet)\s+(" + NUMBER + r")", text
    )
    if m is None:
        raise ValueError("coverage condition not found")
    cov, req = F(m.group(1)), F(m.group(2))
    if not (cov >= req):
        ok = False

    # Boolean flag: "<true|false> indicates that the completed engagement covered both
    # metrics and issued an unmodified conclusion"
    m = re.search(r"\b(true|false)\b\s+indicates", text, flags=re.I)
    if m is None:
        raise ValueError("engagement flag not found")
    if m.group(1).lower() != "true":
        ok = False

    final = "assured" if ok else "review_required"

    slots = {}
    for s in q["trace_spec"]["slots"]:
        sid = s["slot_id"] if "slot_id" in s else s["id"]
        if "lower" in sid:
            slots[sid] = lower_factor
        elif "upper" in sid:
            slots[sid] = upper_factor
        else:
            raise ValueError(f"unknown slot {sid}")
    return {"final": final, "slots": slots}
