"""h046 -- three-year retirement bridge with growing year-end withdrawals.

Structure (identical across the 3 instances; only the numbers differ):
    opening capital P; balance earns r annually (compound, applied to the remaining balance);
    year-end withdrawals  W, W*(1+g), W*(1+g)^2  (g = the "one plus g" growth factor);
    immediately after the third withdrawal a reserve R must remain.  Find W.

Chain (interest for the year accrues first, then the year-end withdrawal is taken):
    B1 = P(1+r)            - W
    B2 = B1(1+r)           - W(1+g)
    B3 = B2(1+r)           - W(1+g)^2   = R
  => P(1+r)^3 - W[(1+r)^2 + (1+g)(1+r) + (1+g)^2] = R
  => W = (P(1+r)^3 - R) / [(1+r)^2 + (1+g)(1+r) + (1+g)^2]

AMBIGUITIES CONSIDERED AND RESOLVED
1. Rate units: "earns 0.04 annually" / "one plus 0.04" are already decimal ratios (no "percent"),
   so they are used as-is.  A defensive fallback divides by 100 only if the word "percent"/"%"
   immediately follows the number.
2. "that growth factor" in "W times the square of that growth factor after year 3" refers to the
   factor just named, "one plus g" -> third withdrawal = W(1+g)^2, NOT W(1+r)^2.  Instance 1 has
   r == g so both readings coincide there; instances 2 and 3 separate the two rates, which shows
   the generator deliberately carries a withdrawal-growth rate distinct from the earning rate.
3. Timing: withdrawals "occur at each year-end" and the "remaining balance earns r annually" ->
   ordinary (end-of-period) withdrawals: interest first, then the withdrawal.  No annuity-due.
4. Reserve condition: "Immediately after the third withdrawal, R must remain" -> B3 == R exactly
   (an equality, not an inequality); no further interest is applied after the third withdrawal.
5. Rounding: "Define the reserve equality using the unrounded exact withdrawal ... the displayed
   amount is a reporting approximation" -> W is solved exactly as a Fraction; the framework rounds
   half-up to 2 dp for display.  No rounding anywhere inside the computation.
6. Checkpoint "gross two-year value of the opening capital before withdrawals" -> the opening
   capital compounded for two years at the earning rate r with NO withdrawals subtracted:
   P(1+r)^2.  "Gross" and "before withdrawals" both exclude W; "of the opening capital" fixes the
   base as P; the growth rate of capital is the earning rate r, not the withdrawal growth g.
   (Not the year-2 balance after the year-1 withdrawal, and not the three-year value P(1+r)^3.)
7. Compounding: "the remaining balance earns r annually" is compound growth on the balance, not
   simple interest, so (1+r)^2 and (1+r)^3 are used.
8. Units: all amounts are USD and the result_spec unit is "usd", so values are returned in plain
   USD (no scaling).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h046"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate anchored on ``pattern``; divide by 100 only if 'percent'/'%' follows it."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    tail = text[m.end(1): m.end(1) + 12]
    if re.match(r"\s*(?:percent|%)", tail):
        value = value / 100
    return value


def solve(text: str, q: dict) -> dict:
    # Opening capital.
    P = grab(r"retirement bridge with\s+{N}", text)
    # Earning rate on the remaining balance (decimal ratio in the text).
    r = _rate(r"balance earns\s+{N}\s+annually", text)
    # Withdrawal growth rate: "W times one plus g after year 2".
    g = _rate(r"one plus\s+{N}", text)
    # Required reserve immediately after the third withdrawal.
    R = grab(r"third withdrawal,?\s+{N}\s+must remain", text)

    a = 1 + r   # balance growth factor per year
    b = 1 + g   # withdrawal growth factor ("that growth factor")

    # Withdrawal multipliers for years 1..3: 1, b, b^2 (exact integer powers of Fractions).
    n_years = 3
    mults = [b ** k for k in range(n_years)]

    # Closed form derived from the chain B_{k} = B_{k-1}*a - W*mults[k-1], B_3 = R:
    #   P*a^3 - W * sum_k mults[k-1] * a^(3-k) = R
    denom = sum(mults[k] * a ** (n_years - 1 - k) for k in range(n_years))
    W = (P * a ** n_years - R) / denom

    # Self-check: replay the exact chain with the unrounded W; must land exactly on R.
    bal = P
    for k in range(n_years):
        bal = bal * a - W * mults[k]
    assert bal == R, "reserve equality not satisfied by exact W"

    two_year_gross = P * a ** 2

    return {
        "final": W,
        "slots": {
            "two_year_gross_capital_checkpoint": two_year_gross,
        },
    }
