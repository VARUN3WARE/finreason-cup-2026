"""h076 -- Tier 1 adjustment x binding on capital vs leverage constraint.

AMBIGUITY HUNT (resolved against the question text):

1. Combined ratio = minimum capital ratio + capital buffer ratio ("Add the minimum
   capital ratio and buffer ratio").  Reported as a plain decimal RATIO (spec unit
   "ratio", e.g. 0.12), NOT percent.  The checkpoint is this sum, unrounded
   (framework rounds half-up to 6 dp); "use its exact unrounded value downstream"
   means we never feed the 6-dp display value into the gap.
2. Total eligible capital = Tier1 + Tier2: the text spells the capital constraint
   as combined_ratio*risk_weighted_assets-(Tier1+Tier2).  Tier 2 is fixed; x
   enters Tier1 and total capital one-for-one, hence both gaps are linear in x.
3. Capital gap   = combined_ratio * RWA - (Tier1 + Tier2)
   Leverage gap  = min_leverage_ratio * total_exposure - Tier1
   x must be >= both ("at least" => non-strict), so the smallest feasible x is
   max(gap_cap, gap_lev).  "Return the larger gap" = algebraic max, NOT the larger
   absolute value: when both gaps are negative the max is the one closer to zero,
   which is exactly the withdrawal that keeps BOTH constraints holding (the text:
   "negative x means the scenario permits withdrawal of -x while both constraints
   still hold").
4. No floor at zero: negative x is explicitly meaningful ("permits withdrawal").
   Zero is "exactly binding" -- it is just the max, no special casing.
5. Ties: both gaps equal => max is that common value; nothing else to decide.
6. Units: every amount is already in USD millions and the answer unit is
   usd_million, so no scaling.  Ratios are "decimal ratios" (0.08 means 8%);
   a defensive percent-detection is included in case a variant words them as
   percent, but the three instances all use decimals.
7. Parsing: "Tier 1" / "Tier 2" contain digits, so every regex is anchored on
   the full phrase ("eligible Tier 1 capital {N}") and the ratios are anchored on
   their distinct names ("minimum capital ratio", "capital buffer ratio",
   "minimum leverage ratio") so the leverage and capital minima cannot be
   confused.
8. No rounding anywhere inside the computation; the final x and the checkpoint
   are returned exact.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h076"


def _grab_any(patterns: list[str], text: str) -> Fraction:
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _ratio(patterns: list[str], text: str) -> Fraction:
    """Grab a ratio; if the matched number is immediately followed by '%' or
    'percent', convert it to a decimal ratio."""
    for p in patterns:
        rx = p.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S)
        if m is None:
            continue
        val = F(m.group(1))
        tail = text[m.end(1): m.end(1) + 12]
        if re.match(r"\s*(?:%|percent)", tail):
            return val / 100
        return val
    raise ValueError(f"none of the ratio patterns matched: {patterns!r}")


_OPT = r"(?:\s+(?:of|is|at|equal\s+to|USD))*\s*"


def solve(text: str, q: dict) -> dict:
    tier1 = _grab_any([
        rf"Tier\s*1 capital{_OPT}{{N}}",
    ], text)
    tier2 = _grab_any([
        rf"Tier\s*2 capital{_OPT}{{N}}",
    ], text)
    rwa = _grab_any([
        rf"risk[- ]weighted assets{_OPT}{{N}}",
    ], text)
    exposure = _grab_any([
        rf"total exposure{_OPT}{{N}}",
    ], text)

    min_cap = _ratio([
        rf"minimum capital ratio{_OPT}{{N}}",
    ], text)
    buffer = _ratio([
        rf"capital buffer ratio{_OPT}{{N}}",
        rf"buffer ratio{_OPT}{{N}}",
    ], text)
    min_lev = _ratio([
        rf"minimum leverage ratio{_OPT}{{N}}",
        rf"leverage ratio{_OPT}{{N}}",
    ], text)

    # Checkpoint: combined capital requirement ratio (plain ratio, unrounded).
    combined = min_cap + buffer

    # Two lower bounds on x; x must satisfy both, so the binding one is the max.
    gap_capital = combined * rwa - (tier1 + tier2)
    gap_leverage = min_lev * exposure - tier1
    x = max(gap_capital, gap_leverage)

    return {
        "final": x,
        "slots": {
            "combined_capital_requirement_ratio_checkpoint": combined,
        },
    }
