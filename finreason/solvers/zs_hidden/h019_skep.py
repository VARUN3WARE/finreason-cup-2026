"""h019 -- common stress capacity of a bank under three regulatory constraints.

Structure (from the text):
  k  = minimum capital ratio + capital buffer ratio                       [checkpoint, ratio, 6 dp]
  x1 = (E  - k  * RWA) / (a + k  * c)      capital constraint
  x2 = (T1 - ml * EXP) / (b + ml * d)      leverage constraint
  x3 = (H  - mq * NCO) / (e + mq * f)      liquidity constraint
  final = min(x1, x2, x3)                                                 [multiple, 2 dp]

AMBIGUITY RESOLUTIONS (recorded before coding):
  1. Pre-breached constraint / negative capacity.  One instance starts with HQLA below the
     required minimum, so its liquidity capacity is negative.  The text says "Return the
     smallest of the three capacities" and gives the three formulas explicitly as the
     capacity definitions.  It words NO floor at zero and NO "positive-only" filter, so the
     literal minimum of the three formula values is returned, even when negative.
     ("Solve exactly for the positive x at which each constraint first binds" describes
     the algebraic step, not a filter -- the formula that follows the colon is the result.)
  2. Unit of k: inputs are "decimal ratios" and the slot unit is "ratio", so
     k = min_capital_ratio + buffer_ratio as a plain ratio (never multiplied by 100).
     If a variant quotes these in percent, they are divided by 100 first.
  3. k is reported as its exact unrounded value (framework applies the 6-dp half-up
     rendering); the exact value is used downstream, exactly as the text instructs
     ("use its exact unrounded value downstream").
  4. Stress coefficients ("decreases eligible capital by 3*x", "reducing HQLA by 0.5*x",
     "increasing risk-weighted assets by 9*x", ...) are positive adverse magnitudes per
     unit of x ("Each stress coefficient is the USD-million adverse change"); they enter
     the stated formulas as positive numbers.  A bare "by x" means a coefficient of 1.
  5. Regex anchoring: starting levels are the number immediately after the noun
     ("risk-weighted assets 971", "total exposure 489", "Tier 1 capital 56.064"),
     while coefficients are the number after "<noun> by".  "Tier 1" contains a digit,
     so its pattern is spelled out literally.
  6. Final unit "multiple" is the plain value of x; no scaling, returned unrounded.
  7. No tie rule is needed: min() of exact Fractions is unambiguous; equal capacities give
     the same value regardless of which constraint "wins".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h019"


def _coef(noun_pattern: str, text: str) -> Fraction:
    """Stress coefficient after '<noun> by': '3*x' -> 3, '0.5*x' -> 1/2, bare 'x' -> 1."""
    m = re.search(noun_pattern + r"\s+by\s+(" + NUMBER + r")\s*\*\s*x\b", text, flags=re.S)
    if m:
        return abs(F(m.group(1)))
    m = re.search(noun_pattern + r"\s+by\s+x\b", text, flags=re.S)
    if m:
        return Fraction(1)
    raise ValueError(f"stress coefficient not found for {noun_pattern!r}")


def _ratio(pattern: str, text: str) -> Fraction:
    """A policy ratio; the text supplies them 'as decimal ratios' (percent guarded anyway)."""
    v = grab(pattern + r"\s*(?:of\s+)?{N}", text)
    m = re.search(pattern + r"\s*(?:of\s+)?" + NUMBER + r"\s*(percent|%)", text, flags=re.S)
    if m:
        v = v / 100
    return v


def solve(text: str, q: dict) -> dict:
    # --- starting balance-sheet levels (USD millions) -------------------------------
    eligible = grab(r"eligible capital\s+(?:of\s+)?{N}", text)
    tier1 = grab(r"Tier\s*1 capital\s+(?:of\s+)?{N}", text)
    rwa = grab(r"risk-weighted assets\s+(?:of\s+)?{N}", text)
    exposure = grab(r"total exposure\s+(?:of\s+)?{N}", text)
    hqla = grab(r"high-quality liquid assets\s+(?:of\s+)?{N}", text)
    nco = grab(r"total net cash outflows\s+(?:of\s+)?{N}", text)

    # --- policy ratios (decimal ratios) ---------------------------------------------
    min_cap = _ratio(r"minimum capital ratio", text)
    buffer = _ratio(r"capital buffer ratio", text)
    min_lev = _ratio(r"minimum leverage ratio", text)
    min_liq = _ratio(r"minimum liquidity ratio", text)

    # --- adverse change per unit of stress activity x (USD millions) ----------------
    a = _coef(r"eligible capital", text)          # eligible capital loss per unit
    b = _coef(r"Tier\s*1 capital", text)          # Tier 1 capital loss per unit
    c = _coef(r"risk-weighted assets", text)      # RWA increase per unit
    d = _coef(r"exposure", text)                  # total exposure increase per unit
    e = _coef(r"HQLA", text)                      # HQLA loss per unit
    f = _coef(r"net cash outflows", text)         # net cash outflow increase per unit

    # --- combined capital requirement ratio k (checkpoint; exact value used downstream)
    k = min_cap + buffer

    # --- capacity at which each constraint first binds (exact rational arithmetic) ---
    cap_capital = (eligible - k * rwa) / (a + k * c)
    cap_leverage = (tier1 - min_lev * exposure) / (b + min_lev * d)
    cap_liquidity = (hqla - min_liq * nco) / (e + min_liq * f)

    # Literal "smallest of the three capacities": no floor, no positive-only filter.
    max_stress = min(cap_capital, cap_leverage, cap_liquidity)

    return {
        "final": max_stress,
        "slots": {"combined_capital_requirement_ratio_checkpoint": k},
    }
