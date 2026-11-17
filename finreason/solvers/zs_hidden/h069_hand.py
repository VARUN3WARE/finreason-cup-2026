from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h069"


def _rate(text: str) -> Fraction:
    m = re.search(r"earns\s+(" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("rate not found")
    r = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        r /= 100
    return r


def solve(text: str, q: dict) -> dict:
    balance = grab(r"saver has (?:USD\s*)?{N}", text)
    contrib = grab(r"one-time contribution of (?:USD\s*)?{N}", text)
    r = _rate(text)

    n_early = grab(r"earlier retirement in {N} years?", text)
    req_early = grab(r"earlier retirement in [^,]*?requires capital of (?:USD\s*)?{N}", text)
    n_late = grab(r"later retirement in {N} years?", text)
    req_late = grab(r"later retirement in [^.]*?requires (?:capital of )?(?:USD\s*)?{N}", text)
    margin = grab(r"exceeds its date-specific requirement by at least (?:USD\s*)?{N}", text)

    principal = balance + contrib
    if n_early.denominator != 1 or n_late.denominator != 1:
        raise ValueError("non-integer horizon")
    g_early = (1 + r) ** int(n_early)
    g_late = (1 + r) ** int(n_late)

    cap_early = principal * g_early
    cap_late = principal * g_late

    feas_early = cap_early - req_early >= margin
    feas_late = cap_late - req_late >= margin

    if feas_early:
        final = "earlier_date"
    elif feas_late:
        final = "later_date"
    else:
        final = "neither_date"

    return {
        "final": final,
        "slots": {
            "earlier_growth_factor_checkpoint": g_early,
            "later_growth_factor_checkpoint": g_late,
        },
    }
