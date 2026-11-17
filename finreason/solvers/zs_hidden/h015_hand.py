"""h015: distributable earnings after retention, n-stage payout ratchet (1-t)^n, capped by liquidity."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h015"

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _stages(text: str) -> int:
    import re
    m = re.search(r"\(1\s*-\s*t\)\s*\^\s*(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"exactly\s+(\w+)\s+sequential", text)
    w = m.group(1).lower()
    return int(w) if w.isdigit() else _WORDS[w]


def solve(text: str, q: dict) -> dict:
    ni = grab(r"net income of {N}", text)
    retain = grab(r"must first retain {N}", text)
    t = grab(r"fraction t\s*=\s*{N}", text)
    cap = grab(r"caps the cash dividend at {N}", text)
    n = _stages(text)

    distributable = ni - retain
    if distributable < 0:
        distributable = Fraction(0)
    one_stage = 1 - t
    policy_limit = distributable * one_stage ** n
    final = min(policy_limit, cap)
    if final < 0:
        final = Fraction(0)
    return {"final": final, "slots": {"one_stage_payout_factor_checkpoint": one_stage}}
