"""h099 -- pre-shock price from a current price after a sequential loss and rebound.

Structure (shared by all 3 instances):
    current price  P_now  (USD per token)
    loss ratio     L      ("reduced its pre-shock price by loss ratio L")
    rebound ratio  R = k * L   ("rebound ratio equal to k times the shock loss ratio")
    P_now = P0 * (1 - L) * (1 + R)      =>   P0 = P_now / ((1 - L) * (1 + k * L))

AMBIGUITIES CONSIDERED AND RESOLUTIONS (textual evidence in quotes):

1. Is the loss multiplicative or an absolute USD reduction?
   "reduced its pre-shock price by loss ratio 0.2" -- a *ratio*, so post-shock = P0 * (1 - L).
   An absolute reduction would be stated in USD.

2. What base does the rebound apply to: the post-shock price, the pre-shock price, or the
   loss amount (partial recovery)?
   "increased the resulting post-shock price by a rebound ratio" and "Apply the loss and
   rebound sequentially" -- the rebound is a proportional increase applied to the
   post-shock price: current = post-shock * (1 + R).  Not P0*(1 - L + R) and not a
   recovery of a fraction of the USD loss.  (Checked numerically: no alternative reading
   yields a "cleaner" pre-shock price, so the literal reading stands.)

3. "increased ... by a rebound ratio R" = multiply by (1 + R), not by R.
   "increased by" a ratio is a relative increase; multiplying by R alone (R < 1) would be
   a further decrease, contradicting "increased".

4. What is the rebound ratio: k or k * L?
   "a rebound ratio equal to 0.4899025 times the shock loss ratio" -- R = k * L.
   The checkpoint "rebound ratio implied by the relative-magnitude input" is therefore
   R = k * L (the relative-magnitude input is k; the ratio it implies is k * L), reported
   as a plain ratio (spec unit "ratio", 6 dp half-up applied by the framework).

5. Rounding: "round only the final price to two decimals" -- nothing is rounded inside
   the computation; P0 and R are returned exact and the framework rounds.

6. Units: prices are in USD per token and the answer unit is "usd" -- returned in USD,
   no scaling.  Ratios are given as plain ratios (0.2, 4/3), not percents; a defensive
   percent fallback is included in case a variant phrases them with "percent"/"%".

7. "What was the price immediately before the shock?" -- P0, i.e. the price before the
   loss was applied (not the post-shock, pre-rebound price).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h099"


def _grab_ratio(patterns: list[str], text: str) -> Fraction:
    """First matching pattern; {N} = number capture.  Percent-phrased variants -> ratio."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is None:
            continue
        val = F(m.group(1))
        tail = text[m.end(1) : m.end(1) + 12]
        if re.match(r"\s*(?:percent|%)", tail, flags=re.I):
            val = val / 100
        return val
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    # Current (post-shock, post-rebound) price in USD per token.
    p_now = _grab_ratio(
        [
            r"currently priced at\s*(?:USD\s*)?{N}",
            r"priced at\s*(?:USD\s*)?{N}",
            r"currently\s+(?:trades|trading)\s+at\s*(?:USD\s*)?{N}",
        ],
        text,
    )

    # Loss ratio L applied to the pre-shock price.
    loss = _grab_ratio(
        [
            r"by\s+(?:a\s+)?loss ratio\s+(?:of\s+|equal to\s+)?{N}",
            r"loss ratio\s+(?:of\s+|equal to\s+)?{N}",
        ],
        text,
    )

    # Relative-magnitude input k: rebound ratio = k * loss ratio.
    k = _grab_ratio(
        [
            r"rebound ratio\s+(?:equal to|of)\s+{N}\s+times\s+the\s+(?:shock\s+)?loss ratio",
            r"rebound ratio\s+(?:equal to|of)\s+{N}\s+times",
            r"rebound ratio\s+(?:equal to|of)\s+{N}",
        ],
        text,
    )

    rebound = k * loss                          # rebound ratio R (plain ratio)
    post_shock_factor = 1 - loss                # pre-shock -> post-shock
    rebound_factor = 1 + rebound                # post-shock -> current
    pre_shock = p_now / (post_shock_factor * rebound_factor)

    return {
        "final": pre_shock,
        "slots": {"rebound_ratio_checkpoint": rebound},
    }
