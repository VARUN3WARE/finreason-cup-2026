"""h075 -- required initial principal given a target FV and one later lump-sum contribution.

Structure (all three instances share it):
    "An account must reach FV USD after n whole annual compounding periods at annual rate ratio r.
     A later contribution of C USD is deposited at a compounding boundary from which exactly m whole
     periods remain, and it earns the same rate. Using exact compounding, what initial principal is
     required at the start?"

Model:
    P * (1+r)^n + C * (1+r)^m = FV
    =>  P = (FV - C * (1+r)^m) / (1+r)^n
Checkpoint "later_contribution_growth_checkpoint" = compound growth factor applied to the later
contribution = (1+r)^m   (unit: multiple).

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
1. Rate units: the text says "annual rate ratio 0.1", so r is already a ratio -- NOT divided by 100.
   (A defensive fallback handles a "percent" phrasing by dividing by 100, but the cluster uses "ratio".)
2. Periods per year: "whole annual compounding periods" -> one compounding per year, rate applied
   once per period; no intra-year compounding and no effective/nominal conversion.
3. Growth factor of the contribution: "deposited at a compounding boundary from which exactly m whole
   periods remain, and it earns the same rate" -> it compounds for exactly m periods: (1+r)^m.
   It is a GROWTH factor (multiple >= 1), not a discount factor 1/(1+r)^m, and not (1+r)^(m-n).
4. m > n in every instance (e.g. n=1, m=5). Physically the deposit date would precede the start, but
   the wording says exactly m periods of growth, so the arithmetic is unchanged: the contribution's
   terminal value is C*(1+r)^m regardless. No capping at n periods (text says "exactly m").
5. Sign / floor: in instances where C*(1+r)^m exceeds FV the required principal is negative. The text
   contains no floor-at-zero wording, so the exact algebraic value is returned (no clamping).
6. Rounding: "Using exact compounding ... round only the final value" -> all Fractions; no rounding of
   the growth factor before use; the framework rounds the final (2 dp) and the checkpoint (6 dp).
7. Integer exponents: n and m are whole numbers -> Fraction ** int (exact), no real_pow.
8. Which value is "required at the start": the principal P at time zero (not the PV of the
   contribution, not the shortfall FV - C*(1+r)^m before discounting).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h075"


def _grab_first(patterns: list[str], text: str) -> Fraction:
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _whole(x: Fraction, name: str) -> int:
    if x.denominator != 1 or x < 0:
        raise ValueError(f"{name} must be a non-negative whole number, got {x}")
    return int(x)


def solve(text: str, q: dict) -> dict:
    # Target future value (USD).
    fv = _grab_first(
        [
            r"must reach\s+{N}\s*USD",
            r"must reach\s+USD\s*{N}",
            r"reach\s+{N}",
        ],
        text,
    )

    # Horizon in whole annual compounding periods.
    n = _whole(
        _grab_first(
            [
                r"after\s+{N}\s+whole\s+annual\s+compounding\s+periods?",
                r"after\s+{N}\s+whole\s+(?:annual\s+)?(?:compounding\s+)?periods?",
                r"after\s+{N}\s+(?:annual\s+)?(?:compounding\s+)?periods?",
            ],
            text,
        ),
        "n",
    )

    # Annual rate: given as a ratio in this cluster; fall back to percent phrasing defensively.
    rate_ratio_pats = [
        r"annual\s+rate\s+ratio\s+(?:of\s+)?{N}",
        r"rate\s+ratio\s+(?:of\s+)?{N}",
    ]
    rate_pct_pats = [
        r"annual\s+rate\s+(?:of\s+)?{N}\s*(?:percent|%)",
        r"rate\s+(?:of\s+)?{N}\s*(?:percent|%)",
    ]
    try:
        r = _grab_first(rate_ratio_pats, text)
    except ValueError:
        r = _grab_first(rate_pct_pats, text) / 100

    # Later contribution amount (USD).
    c = _grab_first(
        [
            r"contribution\s+of\s+{N}\s*USD",
            r"contribution\s+of\s+USD\s*{N}",
            r"contribution\s+of\s+{N}",
        ],
        text,
    )

    # Whole periods the contribution compounds for.
    m = _whole(
        _grab_first(
            [
                r"exactly\s+{N}\s+whole\s+periods?\s+remain",
                r"exactly\s+{N}\s+(?:whole\s+)?(?:compounding\s+)?periods?\s+remain",
                r"{N}\s+whole\s+periods?\s+remain",
            ],
            text,
        ),
        "m",
    )

    growth = Fraction(1) + r
    contrib_factor = growth ** m          # (1+r)^m, exact
    principal_factor = growth ** n        # (1+r)^n, exact

    # P * (1+r)^n + C * (1+r)^m = FV  ->  P = (FV - C*(1+r)^m) / (1+r)^n
    principal = (fv - c * contrib_factor) / principal_factor

    return {
        "final": principal,
        "slots": {
            "later_contribution_growth_checkpoint": contrib_factor,
        },
    }
