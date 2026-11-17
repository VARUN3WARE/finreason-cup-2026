"""h069 -- retirement date choice: earlier vs later date with a surplus cushion.

Literal transcription of the question:
  "A saver has B and can add a one-time contribution of C today."
  "The combined amount earns r annually in the stated scenario."
  "An earlier retirement in n1 years requires capital of R1,
   while a later retirement in n2 years requires R2."
  "Either date is feasible only if projected capital exceeds its date-specific
   requirement by at least M."
  "Prefer the earlier date whenever it is feasible; otherwise choose the later
   date if feasible."  (neither feasible -> neither_date)
Checkpoints: compound growth factor (1+r)^n to each date (plain multiple).
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h069"


def _rate(text: str) -> Fraction:
    m = re.search(rf"earns\s+(?:an?\s+)?(?:annual\s+)?(?:rate\s+of\s+)?({NUMBER})\s*(percent|%)?", text)
    if m is None:
        raise ValueError("rate not found")
    r = Fraction(m.group(1).replace(",", ""))
    if m.group(2):  # stated as a percent
        r = r / 100
    return r


def solve(text: str, q: dict) -> dict:
    # Sentence 1: current savings and the one-time contribution made today.
    savings = grab(r"saver has (?:USD\s*)?\$?{N}", text)
    contribution = grab(r"one-time contribution of (?:USD\s*)?\$?{N}", text)

    # Sentence 2: the combined amount compounds annually at the stated rate.
    combined = savings + contribution
    r = _rate(text)

    # Sentence 3: dates and date-specific capital requirements.
    n_early = grab(r"earlier retirement in {N} years?", text)
    req_early = grab(r"earlier retirement in [^,;]*?requires (?:capital of )?(?:USD\s*)?\$?{N}", text)
    n_late = grab(r"later retirement in {N} years?", text)
    req_late = grab(r"later retirement in [^,;.]*?requires (?:capital of )?(?:USD\s*)?\$?{N}", text)

    # Sentence 4: feasibility cushion -- surplus over requirement must be at least M.
    cushion = grab(r"by at least (?:USD\s*)?\$?{N}", text)

    # Growth factors (checkpoints) and projected capital at each date.
    assert n_early.denominator == 1 and n_late.denominator == 1
    g_early = (1 + r) ** int(n_early)
    g_late = (1 + r) ** int(n_late)
    cap_early = combined * g_early
    cap_late = combined * g_late

    feasible_early = (cap_early - req_early) >= cushion
    feasible_late = (cap_late - req_late) >= cushion

    # Sentence 5: prefer earlier when feasible; else later if feasible; else neither.
    if feasible_early:
        final = "earlier_date"
    elif feasible_late:
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
