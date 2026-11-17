"""Cluster h084 -- degree of financial leverage from two fixed-rate debt tranches.

AMBIGUITY RESOLUTIONS (skeptic pass)
------------------------------------
1. Rate "0.1" is a plain RATIO, not a percent.  The text says "at rate 0.1" with no
   "percent"/"%" token; 0.1 / 0.2 / 0.15 are realistic per-period debt rates whereas
   0.1 % would be absurd.  Defensive: if a "percent" or "%" token immediately follows
   the rate number, divide by 100 (never triggers on the three instances).
2. No period conversion: "All amounts and rates use the same period", so each
   tranche's interest expense is simply debt * rate (simple, single-period interest;
   no annualization, no day-count, no compounding).
3. Checkpoints: "exact-period interest expense from tranche A/B" = debt_X * rate_X in
   USD.  Returned UNROUNDED; the framework applies half-up 4 dp independently
   ("never feed displayed checkpoints into the gold calculation").
4. EBIT reconstruction is explicitly "adding both interest expenses back to earnings
   before tax" under "no other non-operating items, preferred dividends, or tax
   adjustments", so EBIT = EBT + I_A + I_B with nothing else.
5. DFL is explicitly defined in the text as EBIT / EBT (not the EPS/EBIT elasticity
   definition).  Unit "multiple" -> plain ratio, not percent.
6. EBT is stated as "positive ... after deducting all modeled interest expense", i.e.
   it is already net of interest; we add interest back, we do not subtract it again.
   Defensive: if the text literally said "negative earnings before tax of X", the sign
   would be flipped; "positive" (the actual wording) leaves it as-is.
7. Final value is the exact Fraction EBIT / EBT; the framework rounds half-up to 4 dp.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h084"

_NUM = f"({NUMBER})"


def _ebt(text: str) -> Fraction:
    # "... has positive earnings before tax of 5137 USD after deducting ..."
    m = re.search(
        r"(positive|negative)?\s*(?:earnings\s+before\s+tax(?:es)?|EBT|pre-?tax\s+(?:earnings|income))"
        r"\s*(?:\(EBT\))?\s*(?:of|is|are|=|equals?|:)?\s*(?:USD\s*)?" + _NUM,
        text,
        flags=re.I | re.S,
    )
    if m is None:
        raise ValueError("earnings before tax not found")
    value = F(m.group(2))
    sign_word = (m.group(1) or "").lower()
    if sign_word == "negative" and value > 0:
        value = -value
    return value


def _tranche(label: str, text: str) -> tuple[Fraction, Fraction]:
    # "Tranche A debt is 29673.0003 USD at rate 0.1"
    m = re.search(
        rf"[Tt]ranche\s+{label}\s+(?:debt|principal|loan|borrowing)s?\s*"
        rf"(?:is|of|=|equals?|:)?\s*(?:USD\s*)?{_NUM}\s*(?:USD)?\s*"
        rf"(?:at|with|carrying|bearing)?\s*(?:an?\s+)?(?:(?:fixed|interest|periodic|per-period)\s+)*"
        rf"rate\s*(?:of|is|=|:)?\s*{_NUM}\s*(percent|%)?",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError(f"tranche {label} not found")
    debt = F(m.group(1))
    rate = F(m.group(2))
    if m.group(3):
        rate = rate / 100
    return debt, rate


def solve(text: str, q: dict) -> dict:
    ebt = _ebt(text)
    debt_a, rate_a = _tranche("A", text)
    debt_b, rate_b = _tranche("B", text)

    # Single-period simple interest on each tranche (same period as EBT).
    interest_a = debt_a * rate_a
    interest_b = debt_b * rate_b

    # EBT is already net of interest; add both interest expenses back to get EBIT.
    ebit = ebt + interest_a + interest_b

    # Degree of financial leverage as defined in the text: EBIT / EBT (a multiple).
    dfl = ebit / ebt

    return {
        "final": dfl,
        "slots": {
            "tranche_a_interest_checkpoint": interest_a,
            "tranche_b_interest_checkpoint": interest_b,
        },
    }
