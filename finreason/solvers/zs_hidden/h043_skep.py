"""h043 -- inverse WACC: maximum pre-tax cost of debt that keeps WACC at a ceiling.

AMBIGUITY HUNT (resolved against the question text):

1. WACC formula.  Standard after-tax WACC:
       WACC = E/(D+E) * Re + D/(D+E) * Rd * (1 - t)
   The text uses "equity value", "debt value", "cost of equity", "corporate tax
   rate", "pre-tax cost of debt" and "WACC" -- exactly the inputs of the standard
   after-tax formula, so the tax shield (1 - t) applies to the debt term and the
   requested Rd is the PRE-TAX figure (the text says "pre-tax cost of debt").

2. "Maximum ... that keeps its WACC at that ceiling".  WACC is strictly increasing
   in Rd (D > 0, t < 1), so the maximum admissible Rd is the one with WACC
   exactly equal to the ceiling.  Solve the equality:
       Rd = (W * (D + E) - E * Re) / (D * (1 - t))
   Equivalently, in debt-to-equity form with x = D/E:
       Rd = (W * (1 + x) - Re) / (x * (1 - t))
   Both forms are algebraically identical; the solver asserts this.

3. Units.  "cost of equity percentage 12" and "WACC ceiling 10 is also a
   percentage" are percent numbers; "corporate tax rate ratio 0.28" is a plain
   ratio.  The WACC relation is linear in the rates, so keeping Re and W in
   percent yields Rd directly in percent, which is the required answer unit
   ("percent").  The tax rate must be a ratio inside (1 - t); the solver also
   tolerates a "tax rate percentage" phrasing (divides by 100) and a
   "cost of equity ratio" phrasing (multiplies by 100) in case a sibling
   instance is worded differently.

4. Checkpoint "debt-to-equity ratio used by the inverse WACC calculation",
   unit "ratio".  Debt-to-equity is D / E (NOT the debt weight D / (D + E));
   the slot id is debt_to_equity_checkpoint.  Returned unrounded as a plain
   ratio; the framework applies the 6-dp half-up rounding.

5. Rounding.  No sentence says a rounded value is reused downstream, so the
   whole chain is exact Fractions and the final/checkpoint are returned
   unrounded.  (Checked: feeding the 6-dp D/E back in would not change any of
   the three 2-dp answers, but we never do that.)

6. Equity/debt "value" are market values in the same currency unit; only their
   ratio matters, so the unit is irrelevant.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, NUMBER, grab

TEMPLATE_ID = "h043"


def _grab_first(patterns: list[str], text: str) -> Fraction:
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _rate_as_percent(label_patterns: list[str], text: str) -> Fraction:
    """Grab a rate that the text labels as a percentage (default) or a ratio.

    Returns the value in PERCENT units.
    """
    for base in label_patterns:
        m = re.search(base + r"\s*(?:as a |of )?(percentage|percent|ratio)?\s*(?:of )?(" + NUMBER + r")", text, flags=re.S)
        if m:
            kind = (m.group(1) or "").lower()
            val = F(m.group(2))
            if kind == "ratio":
                return val * 100
            return val
    raise ValueError(f"rate not found for {label_patterns!r}")


def _rate_as_ratio(label_patterns: list[str], text: str) -> Fraction:
    """Grab a rate that the text labels as a ratio (default) or a percentage.

    Returns the value as a plain RATIO.
    """
    for base in label_patterns:
        m = re.search(base + r"\s*(?:as a |of )?(percentage|percent|ratio)?\s*(?:of )?(" + NUMBER + r")", text, flags=re.S)
        if m:
            kind = (m.group(1) or "").lower()
            val = F(m.group(2))
            if kind in ("percentage", "percent"):
                return val / 100
            if kind == "":
                # Unlabelled: a tax rate above 1 can only be a percent number.
                return val / 100 if val > 1 else val
            return val
    raise ValueError(f"rate not found for {label_patterns!r}")


def solve(text: str, q: dict) -> dict:
    # Market values of equity and debt (same currency unit; only the ratio matters).
    E = _grab_first([r"equity value(?: of)? {N}", r"equity(?: market)? value(?: is| of)? {N}"], text)
    D = _grab_first([r"debt value(?: of)? {N}", r"debt(?: market)? value(?: is| of)? {N}"], text)

    # Cost of equity in percent (text: "cost of equity percentage 12").
    Re_pct = _rate_as_percent([r"cost of equity"], text)

    # Corporate tax rate as a ratio (text: "corporate tax rate ratio 0.28").
    t = _rate_as_ratio([r"(?:corporate )?tax rate"], text)

    # WACC ceiling in percent (text: "WACC ceiling 10 is also a percentage").
    W_pct = _grab_first([r"WACC ceiling(?: of| is)? {N}", r"ceiling(?: of| is)? {N}"], text)

    if E <= 0 or D <= 0:
        raise ValueError("equity and debt values must be positive")
    if t >= 1:
        raise ValueError(f"tax rate {t} is not a valid ratio")

    # Checkpoint: debt-to-equity ratio D / E (plain ratio, unrounded).
    de_ratio = D / E

    # Inverse WACC: solve  W = E/(D+E)*Re + D/(D+E)*Rd*(1-t)  for Rd (percent units).
    V = D + E
    rd_pct = (W_pct * V - E * Re_pct) / (D * (1 - t))

    # Same thing written in D/E form -- consistency check of the two derivations.
    rd_pct_de = (W_pct * (1 + de_ratio) - Re_pct) / (de_ratio * (1 - t))
    assert rd_pct == rd_pct_de

    # Forward check: plugging Rd back in reproduces the ceiling exactly.
    wacc_check = (E / V) * Re_pct + (D / V) * rd_pct * (1 - t)
    assert wacc_check == W_pct

    return {
        "final": rd_pct,
        "slots": {"debt_to_equity_checkpoint": de_ratio},
    }
