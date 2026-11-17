"""Hidden cluster h090 -- two financing packages tested against a three-stage leverage-covenant ratchet.

AMBIGUITY HUNT -- every point where two analysts could disagree, with the textual resolution:

1. Post-financing balance sheet. "Package X adds equity proceeds of E and debt proceeds of D."
   Proceeds are cash raised: both raise assets; debt proceeds also raise liabilities; equity
   proceeds raise equity. Therefore
       assets_post      = A0 + E + D
       liabilities_post = L0 + D
       equity_post      = assets_post - liabilities_post = (A0 - L0) + E
   Cross-check: reading "post-financing equity" as the equity proceeds E alone fails the
   threshold for every package in every instance (all "Neither package"), implausible for a
   designed cluster; the thresholds (99-108) sit right around (A0 - L0) + E (110-144), which
   confirms the book-equity reading. (The final enum is in fact identical under the alternative
   "debt proceeds do not raise assets" reading as well, so the answer is robust to that point.)

2. Equity test: "post-financing equity is at least X"  ->  equity_post >= X (non-strict).
   Strict wording ("more than", "exceeds", "above") is detected and honoured if it ever appears.

3. Leverage ratio: "exact liabilities-to-assets ratio" -> liabilities_post / assets_post, an exact
   Fraction, dimensionless (every amount is in the same USD-million unit).

4. Ceiling: "ceiling starts at 1.00. At each stage, the company reduces the remaining ceiling by
   the same fraction t, so the final cumulative ceiling is (1-t)^3"  ->  multiplicative ratchet,
   final_ceiling = start * (1 - t) ** n, n = 3 (parsed from "^3", fallback from "three-stage").
   t is a plain fraction (0.1999995), NOT a percent. Exact Fraction arithmetic throughout; the
   rounded checkpoint is never fed back into the chain.

5. Ceiling test: "does not exceed that final inclusive ceiling"  ->  ratio <= ceiling (non-strict,
   "inclusive"). Strict wording ("strictly below", "exclusive") is detected and honoured if present.

6. Selection: among qualifying packages return the one with the lower EXACT ratio; "choose
   Package A on an exact tie" -> A when the two Fractions are equal; "Neither package" when
   no package qualifies. No rounding anywhere in the comparison chain.

7. Checkpoint "one-stage liabilities-to-assets cap factor" (ratio, 6 dp half-up) is the per-stage
   multiplier (1 - t). Because the ceiling starts at 1.00 this equals the ceiling after one stage,
   so both readings coincide. It is NOT t (that is the reduction, not the cap factor) and NOT
   (1-t)^3 (that is the three-stage cumulative ceiling). Returned unrounded; the framework rounds
   (e.g. 1 - 0.1999995 = 0.8000005 -> 0.800001 half-up).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab

TEMPLATE_ID = "h090"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _stages(text: str) -> int:
    """Number of ratchet stages: prefer the explicit exponent in '(1-t)^n', else 'n-stage'."""
    m = re.search(r"\(\s*1\s*-\s*t\s*\)\s*\^\s*(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"\b([a-z]+|\d+)-stage\b", text, flags=re.I)
    if m:
        tok = m.group(1).lower()
        if tok.isdigit():
            return int(tok)
        if tok in _WORD_NUM:
            return _WORD_NUM[tok]
    raise ValueError("could not determine number of ratchet stages")


def _equity_strict(text: str) -> bool:
    """True when the equity threshold is a strict inequality; default (text: 'at least') is non-strict."""
    m = re.search(r"post-financing equity (?:is|of) ([a-z ]+?) ?-?\d", text, flags=re.I)
    phrase = (m.group(1) if m else "at least").strip().lower()
    if re.search(r"\b(strictly|more than|greater than|above|exceeds|over)\b", phrase):
        return True
    return False


def _ratio_strict(text: str) -> bool:
    """True when the ceiling test is strict; default (text: 'does not exceed ... inclusive') is non-strict."""
    m = re.search(r"ratio (does not exceed|is at most|is no more than|is below|is less than|"
                  r"is strictly below|is strictly less than|stays below|is under)", text, flags=re.I)
    phrase = (m.group(1) if m else "does not exceed").lower()
    if "strictly" in phrase or phrase in ("is below", "is less than", "stays below", "is under"):
        return True
    if re.search(r"\bexclusive ceiling\b", text, flags=re.I):
        return True
    return False


def _tie_winner(text: str) -> str:
    m = re.search(r"choose (Package [AB]) on an exact tie", text)
    return m.group(1) if m else "Package A"


def solve(text: str, q: dict) -> dict:
    # --- inputs ------------------------------------------------------------------------------
    a0 = grab(r"assets of {N} and liabilities of {N}", text, 1)
    l0 = grab(r"assets of {N} and liabilities of {N}", text, 2)

    ea = grab(r"Package A adds equity proceeds of {N} and debt proceeds of {N}", text, 1)
    da = grab(r"Package A adds equity proceeds of {N} and debt proceeds of {N}", text, 2)
    eb = grab(r"Package B adds equity proceeds of {N} and debt proceeds of {N}", text, 1)
    db = grab(r"Package B adds equity proceeds of {N} and debt proceeds of {N}", text, 2)

    start_cap = grab(r"ceiling starts at {N}", text)
    t = grab(r"by the same fraction {N}", text)          # plain fraction, not a percent
    n = _stages(text)
    eq_min = grab(r"post-financing equity is (?:at least|more than|greater than|above|exceeds|"
                  r"at or above|no less than|strictly (?:more|greater) than) {N}", text)

    # --- ratchet -----------------------------------------------------------------------------
    one_stage_factor = Fraction(1) - t                    # checkpoint (unrounded)
    final_ceiling = start_cap * one_stage_factor ** n     # exact (1-t)^3 scaled by the 1.00 start

    # --- packages ----------------------------------------------------------------------------
    def evaluate(e: Fraction, d: Fraction) -> tuple[bool, Fraction]:
        assets = a0 + e + d
        liabilities = l0 + d
        equity = assets - liabilities                     # == (a0 - l0) + e
        ratio = liabilities / assets
        eq_ok = equity > eq_min if _equity_strict(text) else equity >= eq_min
        cap_ok = ratio < final_ceiling if _ratio_strict(text) else ratio <= final_ceiling
        return (eq_ok and cap_ok), ratio

    ok_a, ratio_a = evaluate(ea, da)
    ok_b, ratio_b = evaluate(eb, db)

    # --- selection ---------------------------------------------------------------------------
    if ok_a and ok_b:
        if ratio_a < ratio_b:
            final = "Package A"
        elif ratio_b < ratio_a:
            final = "Package B"
        else:
            final = _tie_winner(text)
    elif ok_a:
        final = "Package A"
    elif ok_b:
        final = "Package B"
    else:
        final = "Neither package"

    return {
        "final": final,
        "slots": {"one_stage_leverage_cap_checkpoint": one_stage_factor},
    }
