"""h003 -- shared cost pool allocation that equalises two segments' after-tax profit margins.

AMBIGUITY RESOLUTIONS (recorded before implementation):

1. "after-tax profit margin ratios" -> after-tax profit divided by segment REVENUE (a margin is
   profit/revenue; "ratios" is just the plural for the two segments' margins). It is NOT
   after-tax / pre-tax profit (that would be the constant 1 - t and could never be equalised by x).
2. The pool is a "shared DEDUCTIBLE cost pool" and the given margins are "before allocating" it, so
   the allocated share reduces PRE-TAX profit first, and the tax rate is then applied to the
   post-allocation pre-tax profit:   AT_i = (1 - t_i) * (m_i * R_i - alloc_i).
3. "each tax rate is applied to the resulting positive pre-tax profit": the text asserts the
   post-allocation profits are positive, so tax is linear.  Defensive generalisation only: if a
   post-allocation pre-tax profit were a loss, no tax would be levied on it (tax applies to positive
   profit).  The equation is then piecewise linear; we solve every regime exactly and keep the one
   that is self-consistent.  For all three instances both profits are positive, so this collapses
   to the plain closed form.
4. Checkpoints: "the shared cost pool as a ratio of Segment A/B revenue" = WHOLE pool / revenue
   (C/R_A, C/R_B).  Not the allocated share x*C/R (the description says "the shared cost pool", and
   the checkpoints sit at positions 1-2, before x is known -- they are the coefficients of x in the
   equality equation).  Unit "ratio": plain fraction, returned unrounded.
5. Units: margins and tax rates are given as decimals (0.46875, 0.2) -> used as-is.  If a variant
   ever wrote "percent"/"%", the parser divides by 100.  The final answer is "percentage x" with
   result unit percent -> return 100 * x (x = fraction of the pool allocated to A).
6. No clamp of x to [0, 1] is stated; we return the exact value that equalises the margins.
   (All three instances fall strictly inside (0, 1).)
7. "Allocate ... exactly once": A gets x*C, B gets (1-x)*C; nothing is double-counted or taxed twice.

Closed form (both profits positive):
    (1-tA)(mA - x*a) = (1-tB)(mB - (1-x)*b),   a = C/R_A,  b = C/R_B
    x = [(1-tA)*mA - (1-tB)*mB + (1-tB)*b] / [(1-tA)*a + (1-tB)*b]
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h003"


# A number capture followed by an optional percent tag.  NUMBER has a top-level alternation, so it
# MUST be wrapped in a group before being embedded in a larger pattern.
_NUM_UNIT = rf"((?:{NUMBER}))(\s*(?:percent|%))?"


def _val(num: str, unit: str | None) -> Fraction:
    v = F(num)
    if unit:
        v /= 100
    return v


def _rate(text: str, pattern: str) -> Fraction:
    """Capture a number via ``pattern`` (with {N}); divide by 100 if it is tagged percent/%."""
    rx = pattern.replace("{N}", _NUM_UNIT)
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return _val(m.group(1), m.group(2))


def _segment(text: str, name: str) -> tuple[Fraction, Fraction, Fraction]:
    """(revenue, pre-shared-cost pre-tax margin, tax rate) for 'Segment <name> has revenue R, ...'."""
    rx = (
        rf"Segment {name} has revenue\s+{_NUM_UNIT},?\s*"
        rf"pre-shared-cost pre-tax profit margin\s+{_NUM_UNIT},?\s*"
        rf"and tax rate\s+{_NUM_UNIT}"
    )
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"segment {name} sentence not found")
    rev = _val(m.group(1), m.group(2))
    margin = _val(m.group(3), m.group(4))
    tax = _val(m.group(5), m.group(6))
    return rev, margin, tax


def solve(text: str, q: dict) -> dict:
    r_a, m_a, t_a = _segment(text, "A")
    r_b, m_b, t_b = _segment(text, "B")
    pool = _rate(text, r"shared deductible cost pool of\s+{N}")

    # Pre-allocation pre-tax profits (margins are after segment-specific costs, before the pool).
    p_a = m_a * r_a
    p_b = m_b * r_b

    # Checkpoints: the whole shared pool as a ratio of each segment's revenue.
    burden_a = pool / r_a
    burden_b = pool / r_b

    def after_tax_margin(x: Fraction, taxed_a: bool, taxed_b: bool) -> tuple[Fraction, Fraction]:
        pre_a = p_a - x * pool
        pre_b = p_b - (1 - x) * pool
        at_a = pre_a * ((1 - t_a) if taxed_a else 1)
        at_b = pre_b * ((1 - t_b) if taxed_b else 1)
        return at_a / r_a, at_b / r_b

    def solve_regime(taxed_a: bool, taxed_b: bool) -> Fraction | None:
        ka = (1 - t_a) if taxed_a else Fraction(1)
        kb = (1 - t_b) if taxed_b else Fraction(1)
        # ka*(mA - x*a) = kb*(mB - (1-x)*b)
        denom = ka * burden_a + kb * burden_b
        if denom == 0:
            return None
        x = (ka * m_a - kb * m_b + kb * burden_b) / denom
        pre_a = p_a - x * pool
        pre_b = p_b - (1 - x) * pool
        # Regime consistency: tax applies to positive pre-tax profit, none on a loss.
        ok_a = (pre_a > 0) if taxed_a else (pre_a <= 0)
        ok_b = (pre_b > 0) if taxed_b else (pre_b <= 0)
        return x if (ok_a and ok_b) else None

    # Primary (stated) case: both post-allocation pre-tax profits positive, both taxed.
    x = solve_regime(True, True)
    if x is None:
        for regime in ((True, False), (False, True), (False, False)):
            x = solve_regime(*regime)
            if x is not None:
                break
    if x is None:
        # Degenerate: fall back to the stated linear form regardless of sign.
        x = ((1 - t_a) * m_a - (1 - t_b) * m_b + (1 - t_b) * burden_b) / (
            (1 - t_a) * burden_a + (1 - t_b) * burden_b
        )

    return {
        "final": x * 100,
        "slots": {
            "segment_a_shared_cost_burden_ratio_checkpoint": burden_a,
            "segment_b_shared_cost_burden_ratio_checkpoint": burden_b,
        },
    }
