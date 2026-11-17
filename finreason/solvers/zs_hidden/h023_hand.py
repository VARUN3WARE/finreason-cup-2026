"""h023: two capital plans vs. a multi-stage leverage-covenant ratchet ceiling."""
from fractions import Fraction
import re

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h023"

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
          "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _stages(text: str) -> int:
    m = re.search(r"\(1-t\)\^(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(\w+)-stage", text)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        if w.isdigit():
            return int(w)
    raise ValueError("stage count not found")


def _plan(seg: str, d0: Fraction, e0: Fraction):
    d, e = d0, e0
    m = re.search(r"(?:adds|add) borrowing (-?\d+(?:\.\d+)?(?:/\d+)?)", seg)
    if m:
        d += F(m.group(1))
    m = re.search(r"repays? debt (-?\d+(?:\.\d+)?(?:/\d+)?)", seg)
    if m:
        d -= F(m.group(1))
    m = re.search(r"(?:adds|add)?\s*equity (-?\d+(?:\.\d+)?(?:/\d+)?)", seg)
    if m:
        e += F(m.group(1))
    return d, e


def solve(text: str, q: dict) -> dict:
    d0 = grab(r"current debt {N}", text)
    e0 = grab(r"current equity {N}", text)
    start = grab(r"ceiling starts at {N}", text)
    t = grab(r"fraction t={N}", text)
    n = _stages(text)

    one_stage = start * (1 - t)
    ceiling = start * (1 - t) ** n

    ia = text.index("Plan A")
    ib = text.index("Plan B")
    iend = text.index("A plan qualifies")
    seg_a = text[ia:ib]
    seg_b = text[ib:iend]
    da, ea = _plan(seg_a, d0, e0)
    db, eb = _plan(seg_b, d0, e0)
    ra = da / ea
    rb = db / eb

    qa = ra <= ceiling
    qb = rb <= ceiling
    if qa and qb:
        final = "plan_a" if ra <= rb else "plan_b"
    elif qa:
        final = "plan_a"
    elif qb:
        final = "plan_b"
    else:
        final = "neither_plan"

    return {"final": final,
            "slots": {"one_stage_leverage_cap_checkpoint": one_stage}}
