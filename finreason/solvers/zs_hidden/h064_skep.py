"""h064 -- green-bond structure A vs structure B: compound financing cost + eligibility feasibility.

AMBIGUITY HUNT (each point resolved with textual evidence):

 1. "annual yield ratio 0.05" -- a RATIO, not a percent. The word "ratio" and the magnitudes (0.05, 0.1, 0.02)
    settle it: used directly as r, never divided by 100. (Defensive: if the yield were ever worded as
    "percent", the parser divides by 100.)
 2. "compound the principal over its term" -- compound (not simple) interest, annual compounding, one period
    per year of term: FV = P * (1 + r) ** n. Term is an integer number of years in all instances, so the power is
    exact (Fraction ** int); a non-integer term would fall back to real_pow (never needed here).
 3. "subtract principal to obtain interest cost" -- interest = FV - P (NOT the full FV, NOT simple interest P*r*n).
 4. "add issuance cost to obtain total financing cost" -- total = interest + issuance cost. No rounding anywhere
    in the text, so everything stays exact.
 5. "feasible only if total financing cost does not exceed X" -- NON-strict: total <= X is feasible, total == X is
    still feasible ("does not exceed" = "is not greater than").
 6. "its eligible share reaches Y" -- NON-strict: share >= Y ("reaches" includes equality).
 7. Both conditions are joined by "and" -- a structure must pass BOTH to be feasible.
 8. "Choose the lower-cost feasible structure" -- "cost" is the total financing cost defined in the previous
    sentence (interest + issuance), not issuance cost alone and not interest alone.
 9. "prefer structure_a on a cost tie" -- when both are feasible and totals are exactly equal, return structure_a.
    Implemented as: both feasible -> structure_a iff total_A <= total_B (exact Fraction comparison).
10. "choose the sole feasible structure" -- if exactly one passes, pick it regardless of cost.
11. "return no_feasible_structure when neither qualifies" -- neither passes -> no_feasible_structure.
12. Checkpoint "one-period gross compound factor for structure A", unit "multiple":
    "one-period" => a single (annual) period, NOT the full-term factor (1+r)^n;
    "gross" => 1 + r, NOT the net rate r. So the slot is exactly 1 + r_A, returned UNROUNDED (framework applies
    half-up to 8 dp; e.g. r_A = 0.098400005 renders as 1.09840001, which a float solver would get wrong).
13. The checkpoint is independent of the branch outcome; it is reported for structure A even when A is infeasible.
14. Eligible-proceeds share threshold (0.6) and cost cap are instance values parsed from the text; the share values
    (0.8 / 0.4) are ratios compared directly against the ratio threshold.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, real_pow

TEMPLATE_ID = "h064"

_NUM = f"({NUMBER})"


def _search(pattern: str, text: str) -> Fraction:
    m = re.search(pattern.replace("{N}", _NUM), text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return F(m.group(1))


def _segment(text: str, label: str) -> str:
    """The clause describing one structure, from 'Structure <label> has' to the next structure / next sentence."""
    m = re.search(rf"Structure\s+{label}\s+has\b", text, flags=re.I)
    if m is None:
        raise ValueError(f"structure {label} not found")
    start = m.end()
    # End at whichever comes first: the other structure's clause, or the "For each structure" sentence.
    ends = []
    for marker in (r"Structure\s+[AB]\s+has\b", r"For each structure", r"A structure is feasible"):
        e = re.search(marker, text[start:], flags=re.I)
        if e is not None:
            ends.append(start + e.start())
    end = min(ends) if ends else len(text)
    return text[start:end]


def _structure(text: str, label: str) -> dict:
    seg = _segment(text, label)
    rate = _search(r"annual\s+yield\s+ratio\s+(?:of\s+)?{N}", seg)
    # Defensive: a "percent" wording would need /100; the actual template says "ratio".
    if re.search(r"annual\s+yield\s+(?:ratio\s+)?(?:of\s+)?" + _NUM + r"\s*(?:percent|%)", seg, flags=re.I):
        rate = rate / 100
    term = _search(r"\bterm\s+(?:of\s+)?{N}", seg)
    issuance = _search(r"issuance\s+cost\s+(?:of\s+)?{N}", seg)
    share = _search(r"eligible[-\s]proceeds\s+share\s+(?:of\s+)?{N}", seg)
    return {"rate": rate, "term": term, "issuance": issuance, "share": share}


def _compound(principal: Fraction, rate: Fraction, term: Fraction) -> Fraction:
    base = 1 + rate
    if term.denominator == 1:
        return principal * base ** int(term)
    return principal * real_pow(base, term)  # non-integer term: not expected in this template


def _total_cost(principal: Fraction, s: dict) -> Fraction:
    fv = _compound(principal, s["rate"], s["term"])
    interest = fv - principal
    return interest + s["issuance"]


def solve(text: str, q: dict) -> dict:
    principal = _search(r"principal\s+(?:of\s+)?{N}", text)
    a = _structure(text, "A")
    b = _structure(text, "B")
    cap = _search(r"total\s+financing\s+cost\s+does\s+not\s+exceed\s+{N}", text)
    share_min = _search(r"eligible\s+share\s+reaches\s+{N}", text)

    total_a = _total_cost(principal, a)
    total_b = _total_cost(principal, b)

    # "does not exceed" -> <= ; "reaches" -> >=
    feas_a = total_a <= cap and a["share"] >= share_min
    feas_b = total_b <= cap and b["share"] >= share_min

    if feas_a and feas_b:
        final = "structure_a" if total_a <= total_b else "structure_b"  # tie -> structure_a
    elif feas_a:
        final = "structure_a"
    elif feas_b:
        final = "structure_b"
    else:
        final = "no_feasible_structure"

    return {
        "final": final,
        "slots": {
            # one-period gross compound factor for structure A = 1 + r_A (unrounded; framework rounds half-up 8dp)
            "structure_a_annual_factor_checkpoint": 1 + a["rate"],
        },
    }
