"""h104 -- two financing scenarios: WACC limit + stage-reduced leverage covenant.

FINANCE MODEL (written before the code)
=======================================
Quantity being decided
    Which of two financing scenarios (A, B) is the better *qualifying* one, where a
    scenario qualifies only if it passes BOTH tests below; among qualifying scenarios the
    one with the lower exact WACC wins (exact tie -> "Scenario A"); nobody qualifies ->
    "Neither scenario".

Inputs and how each enters
    Tc   = "corporate tax rate ratio"   -> a plain ratio (0.25 means 25%), used only in the
                                           debt tax shield factor (1 - Tc).
    Wmax = "maximum permitted WACC percentage" -> PERCENT (12 means 12%); compared with the
                                           scenario WACC expressed in the same percent units.
    t    = covenant stage reduction fraction (ratio, e.g. 0.2 = 20% cut per stage).
    n    = number of sequential covenant stages (stated as "exactly three" and as (1-t)^3).
    For each scenario X in {A, B}:
        E  = equity value (market value of equity)        [same currency units as D]
        D  = debt value   (market value of debt)
        Re = cost of equity percentage                    [percent]
        Rd = pre-tax cost of debt percentage              [percent]

Standard finance conventions used (no overrides of the textbook formulas)
    V        = D + E
    WACC_X   = (E/V) * Re + (D/V) * Rd * (1 - Tc)          [percent, same unit as Re, Rd]
               (Modigliani-Miller with corporate tax: only the debt leg is tax-shielded;
                weights are market-value weights built from the stated equity/debt values.)
    DebtRatio_X = D / (D + E)                              [ratio]  -- explicitly NOT D/E.

Stated overrides / scenario-specific policy (taken from the text, "fictional" so no real law)
    * Leverage covenant ceiling starts at 1.00 and is cut MULTIPLICATIVELY by the same
      fraction t at each of n = 3 stages:  ceiling_k = ceiling_{k-1} * (1 - t).
      After one stage the remaining ceiling is 1.00 * (1 - t)  <- checkpoint slot (ratio).
      Final shared ceiling = (1 - t)^3  (stated explicitly in the text).  The same final ceiling
      applies to both scenarios.
    * Inclusive limits: "maximum permitted WACC" -> WACC <= Wmax qualifies;
      "permitted ceiling" -> DebtRatio <= final ceiling qualifies.
      (None of the three instances sits exactly on either boundary, so the inclusive reading
      is only a convention, but it is the natural reading of "maximum"/"ceiling" limits.)
    * Qualification:  qualifies_X = (WACC_X <= Wmax) AND (DebtRatio_X <= final ceiling).
    * Selection: both qualify -> lower exact WACC (A on an exact tie); one qualifies -> that
      one; none -> "Neither scenario".

Exactness
    Everything is exact Fraction arithmetic (the instances use up to ~24-digit decimals, so
    floats would be unsafe).  The checkpoint 1 - t is returned UNROUNDED; the framework applies
    half-up to 6 places (e.g. 1 - 0.1999995 = 0.8000005 -> 0.800001).  No value is rounded
    inside the computation (the text never says a rounded value is reused downstream).

Checkpoint slot
    one_stage_debt_ratio_cap_checkpoint = start_ceiling * (1 - t)   [ratio]
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h104"

SLOT_ID = "one_stage_debt_ratio_cap_checkpoint"

_WORD_COUNTS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _scenario(text: str, label: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """(equity value, debt value, cost of equity %, pre-tax cost of debt %) of one scenario."""
    m = re.search(rf"Scenario {label} has(.*?)\.(?=\s|$)", text, flags=re.S)
    if m is None:
        raise ValueError(f"scenario {label} sentence not found")
    seg = m.group(1)
    equity = grab(r"equity value {N}", seg)
    debt = grab(r"debt value {N}", seg)
    cost_equity = grab(r"cost of equity percentage {N}", seg)
    cost_debt = grab(r"pre-tax cost of debt percentage {N}", seg)
    return equity, debt, cost_equity, cost_debt


def _stage_count(text: str) -> int:
    """Number of sequential covenant stages (final ceiling is (1-t)^n)."""
    m = re.search(r"\(1\s*-\s*t\)\s*\^\s*(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"exactly\s+(\w+)\s+sequential\s+covenant\s+stages", text)
    if m:
        word = m.group(1).lower()
        if word.isdigit():
            return int(word)
        return _WORD_COUNTS[word]
    raise ValueError("number of covenant stages not found")


def solve(text: str, q: dict) -> dict:
    tax = grab(r"corporate tax rate ratio {N}", text)  # ratio
    wacc_cap_pct = grab(r"maximum permitted WACC percentage {N}", text)  # percent
    t = grab(r"same fraction t\s*=\s*{N}", text)  # ratio
    start_ceiling = grab(r"ceiling starts at {N}", text)  # 1.00
    stages = _stage_count(text)

    # --- covenant ceiling: multiplicative cut by t at each stage -----------------------------
    one_stage_ceiling = start_ceiling * (1 - t)
    final_ceiling = start_ceiling * (1 - t) ** stages

    # --- scenario metrics (exact) -------------------------------------------------------------
    results = {}
    for label in ("A", "B"):
        equity, debt, re_pct, rd_pct = _scenario(text, label)
        value = equity + debt
        # WACC in percent: (E/V) Re + (D/V) Rd (1 - Tc)
        wacc_pct = (equity / value) * re_pct + (debt / value) * rd_pct * (1 - tax)
        debt_ratio = debt / value  # D/(D+E)
        qualifies = (wacc_pct <= wacc_cap_pct) and (debt_ratio <= final_ceiling)
        results[label] = (qualifies, wacc_pct)

    qa, wa = results["A"]
    qb, wb = results["B"]
    if qa and qb:
        final = "Scenario A" if wa <= wb else "Scenario B"  # exact tie -> A
    elif qa:
        final = "Scenario A"
    elif qb:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    return {"final": final, "slots": {SLOT_ID: one_stage_ceiling}}
