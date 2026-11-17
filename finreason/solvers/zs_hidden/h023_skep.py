"""Hidden cluster h023 -- two capital plans vs. a three-stage leverage-covenant ratchet.

AMBIGUITY HUNT (resolved from the question text; recorded before coding)
-----------------------------------------------------------------------
A1. "reduces the remaining ceiling by the same fraction t" -- multiplicative or
    subtractive?  Text states explicitly "the final shared ceiling is (1-t)^3",
    so each stage multiplies the remaining ceiling by (1-t).  After one stage the
    remaining ceiling is start * (1-t)^1.  (With start = 1.00 both readings give
    the same first-stage value anyway; the final ceiling is unambiguously (1-t)^3.)
A2. Checkpoint "leverage ceiling remaining after one covenant-ratchet stage" --
    the ceiling (a ratio, not a percent) after exactly ONE of the three stages:
    start * (1-t).  Returned unrounded; the framework applies half_up to 6 dp
    (e.g. t = 0.1999995 -> 0.8000005 -> 0.800001).  Never (1-t)^3 and never the
    reduction amount t itself.
A3. Starting ceiling: parsed from "ceiling starts at {N}" (1.00) rather than
    assumed, and the number of stages is parsed from the "^{N}" exponent (fallback:
    the "<word>-stage" phrase).  Final ceiling = start * (1-t)^n.
A4. t is a plain fraction ("fraction t=0.1999995"), NOT a percent -- no /100.
A5. Plan A "adds borrowing b and equity e": post-transaction debt = D0 + b,
    equity = E0 + e.  Plan B "repays debt r and adds equity e": debt = D0 - r,
    equity = E0 + e.  Repaying debt does not reduce book equity (cash goes out
    against the liability); the equity line changes only by the equity added.
A6. Ratio compared is debt-to-equity = debt / equity (the covenant is a
    "debt-to-equity ceiling"), exact rational, no rounding before comparison.
A7. "qualifies only when its exact post-transaction ratio does not exceed the
    final ceiling" -> non-strict: ratio <= (1-t)^n.  Compared with exact Fractions.
A8. Selection: among qualifying plans pick the lower exact ratio; exact tie ->
    plan_a; only one qualifies -> that one; none -> neither_plan.
A9. Equity is positive in all instances; a non-positive post-transaction equity
    would make the ratio meaningless -- treated as not qualifying (defensive only).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h023"

_WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stages(text: str) -> int:
    """Number of ratchet stages: prefer the explicit exponent in '(1-t)^n'."""
    m = re.search(r"\(\s*1\s*-\s*t\s*\)\s*\^\s*(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\w+)-stage", text, flags=re.I)
    if m:
        w = m.group(1).lower()
        if w in _WORD_NUMS:
            return _WORD_NUMS[w]
        if w.isdigit():
            return int(w)
    raise ValueError("number of ratchet stages not found")


def _plan_sentence(text: str, label: str) -> str:
    m = re.search(rf"Plan {label}\b([^.]*?)\.(?:\s|$)", text, flags=re.S)
    if m is None:
        raise ValueError(f"Plan {label} sentence not found")
    return m.group(1)


def _plan_deltas(sent: str) -> tuple[Fraction, Fraction]:
    """(delta_debt, delta_equity) for one plan sentence (generic verbs)."""
    d_debt = Fraction(0)
    d_eq = Fraction(0)
    n = f"({NUMBER})"
    # Debt increases
    for m in re.finditer(rf"(?:adds?|raises?|issues?|takes? on|increases?)\s+(?:new\s+)?(?:borrowing|debt)\s+(?:of\s+)?{n}", sent):
        d_debt += F(m.group(1))
    # Debt decreases
    for m in re.finditer(rf"(?:repays?|retires?|reduces?|pays? down|pays? off)\s+(?:debt|borrowing)\s+(?:of\s+)?{n}", sent):
        d_debt -= F(m.group(1))
    # Equity increases: "adds equity 101", "and equity 197", "adds borrowing 21 and equity 197"
    for m in re.finditer(rf"(?:adds?|raises?|issues?|and|injects?|increases?)\s+(?:new\s+)?equity\s+(?:of\s+)?{n}", sent):
        d_eq += F(m.group(1))
    # Equity decreases (defensive; not present in the seen instances)
    for m in re.finditer(rf"(?:buys? back|repurchases?|reduces?|retires?)\s+equity\s+(?:of\s+)?{n}", sent):
        d_eq -= F(m.group(1))
    return d_debt, d_eq


def solve(text: str, q: dict) -> dict:
    d0 = grab(r"current debt\s+{N}", text)
    e0 = grab(r"current equity\s+{N}", text)
    start = grab(r"ceiling starts at\s+{N}", text)
    t = grab(r"\bt\s*=\s*{N}", text)                      # plain fraction (A4)
    n = _stages(text)

    one_stage_cap = start * (1 - t)                       # A1/A2 checkpoint
    final_cap = start * (1 - t) ** n                      # A3

    da_debt, da_eq = _plan_deltas(_plan_sentence(text, "A"))
    db_debt, db_eq = _plan_deltas(_plan_sentence(text, "B"))
    if (da_debt, da_eq) == (0, 0) or (db_debt, db_eq) == (0, 0):
        raise ValueError("plan transactions not parsed")

    def ratio(debt: Fraction, eq: Fraction):
        if eq <= 0:
            return None                                   # A9
        return debt / eq

    ra = ratio(d0 + da_debt, e0 + da_eq)                  # A5/A6
    rb = ratio(d0 + db_debt, e0 + db_eq)

    qa = ra is not None and ra <= final_cap               # A7 (non-strict)
    qb = rb is not None and rb <= final_cap

    if qa and qb:                                         # A8
        final = "plan_a" if ra <= rb else "plan_b"        # tie -> plan_a
    elif qa:
        final = "plan_a"
    elif qb:
        final = "plan_b"
    else:
        final = "neither_plan"

    return {"final": final, "slots": {"one_stage_leverage_cap_checkpoint": one_stage_cap}}
