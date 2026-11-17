"""h045 -- ESG program A vs B: net cost per effective ton, feasibility screen, selection.

AMBIGUITY HUNT (resolved against the text):

1. CHECKPOINT QUANTITY ("program A net cost after financial benefits", unit usd, 2dp half_up):
   The text defines two "net cost" quantities: (cost minus financial benefit) and
   "net cost per effective ton". The slot's unit is "usd" (not usd per ton) and the
   description says "net cost after financial benefits" -> it is cost_A - benefit_A,
   NOT the per-ton figure. Reported for program A regardless of its feasibility.

2. OVERLAP RATIO UNIT: given as "attribution-overlap ratio 0.2" -> already a ratio;
   "one minus the overlap ratio" = 1 - 0.2 = 0.8. Guard: if a variant ever writes
   "20 percent"/"20%", divide by 100 (not seen in these instances).

3. WHICH "COST" THE FEASIBILITY CAP APPLIES TO: "its cost does not exceed X" uses the
   named input "cost" (gross cost), not the net cost (which the text always spells out
   as "cost minus financial benefit"). -> gross cost <= cap.

4. STRICTNESS: "does not exceed X" -> cost <= X (non-strict);
   "reaches Y" -> effective reduction >= Y (non-strict).
   The reduction threshold applies to EFFECTIVE reduction (text: "its effective
   reduction reaches"), not verified reduction (instance 3 is a trap: verified 98 vs
   threshold 99 -- but effective 78.4 fails either way; implemented on effective).

5. SELECTION: among feasible programs, the one with LOWER net cost per effective ton
   wins (arithmetically lower, negatives allowed if benefit > cost); exact tie ->
   program_a. Exactly one feasible -> that one. None -> no_feasible_program.
   The per-ton comparison is only reached when BOTH are feasible.

6. ROUNDING: nothing in the text says any intermediate is rounded before use;
   all values stay exact Fractions, framework rounds the checkpoint.

7. PARSING: program A's parameters sit between "program A" and "against program B";
   program B's sit between "program B" and the next "For each program" sentence.
   Each field is anchored on its label within its own section, so field order inside
   a section does not matter.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h045"

PROGRAM_A = "program_a"
PROGRAM_B = "program_b"
NONE_FEASIBLE = "no_feasible_program"


def _section(text: str, start_pat: str, end_pat: str | None) -> str:
    m = re.search(start_pat, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"section start not found: {start_pat!r}")
    start = m.end()
    end = len(text)
    if end_pat is not None:
        m2 = re.search(end_pat, text[start:], flags=re.S | re.I)
        if m2 is not None:
            end = start + m2.start()
    return text[start:end]


def _field(section: str, label_pat: str) -> Fraction:
    """Number right after the label; converts a trailing percent/% to a ratio."""
    rx = rf"{label_pat}\s*(?:of|is|=|:)?\s*(?:USD\s*|\$)?({NUMBER})(\s*(?:percent|%))?"
    m = re.search(rx, section, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"field not found: {label_pat!r} in {section!r}")
    value = F(m.group(1))
    if m.group(2):
        value = value / 100
    return value


def _program(section: str) -> dict:
    cost = _field(section, r"\bcost\b")
    benefit = _field(section, r"financial benefit")
    verified = _field(section, r"verified emissions? reduction")
    overlap = _field(section, r"attribution[- ]overlap ratio")
    effective = verified * (1 - overlap)
    net_cost = cost - benefit
    return {
        "cost": cost,
        "benefit": benefit,
        "verified": verified,
        "overlap": overlap,
        "effective": effective,
        "net_cost": net_cost,
    }


def _per_ton(p: dict) -> Fraction | None:
    if p["effective"] == 0:
        return None  # undefined; only reachable if the reduction threshold is <= 0
    return p["net_cost"] / p["effective"]


def solve(text: str, q: dict) -> dict:
    sec_a = _section(text, r"program A\b", r"(?:against|versus|vs\.?|and)\s+program B\b")
    sec_b = _section(text, r"program B\b", r"\.\s+For each program")
    a = _program(sec_a)
    b = _program(sec_b)

    # Feasibility thresholds (non-strict in both directions per the wording).
    try:
        cost_cap = grab(r"cost does not exceed {N}", text)
    except ValueError:
        cost_cap = grab(r"cost (?:is )?(?:at most|no more than|not more than|not above) {N}", text)
    try:
        red_min = grab(r"effective reduction reaches {N}", text)
    except ValueError:
        red_min = grab(
            r"effective reduction (?:is )?(?:at least|reaches at least|meets or exceeds|no less than) {N}",
            text,
        )

    def feasible(p: dict) -> bool:
        return p["cost"] <= cost_cap and p["effective"] >= red_min

    fa, fb = feasible(a), feasible(b)

    if fa and fb:
        pa, pb = _per_ton(a), _per_ton(b)
        if pa is None and pb is None:
            final = PROGRAM_A  # both undefined -> treat as tie, prefer program_a
        elif pa is None:
            final = PROGRAM_B
        elif pb is None:
            final = PROGRAM_A
        elif pb < pa:
            final = PROGRAM_B
        else:
            final = PROGRAM_A  # strictly lower for A, or exact tie -> program_a
    elif fa:
        final = PROGRAM_A
    elif fb:
        final = PROGRAM_B
    else:
        final = NONE_FEASIBLE

    return {
        "final": final,
        "slots": {"program_a_net_cost_checkpoint": a["net_cost"]},
    }
