"""h057 -- unit gross-profit retention after a price discount and a unit-cost change.

Structure (all three instances):
    original unit price P (USD); baseline gross margin ratio m "calculated from that same undiscounted unit price";
    selling price discounted by d "of the original price"; post-change unit cost C (USD, absolute);
    final  = retention percentage of the original per-unit gross profit;
    slot   = discounted selling price per unit (before subtracting unit cost), USD, 4 dp half-up.

AMBIGUITY HUNT -- points where two analysts could disagree, and the resolution taken:

1. What is "baseline gross margin ratio"?  Margin (profit / price) vs markup (profit / cost).
   Text: "calculated from that same undiscounted unit price and the same per-unit accounting basis" -> the ratio's
   denominator is the undiscounted price P.  Baseline unit gross profit GP0 = m * P.  (Baseline unit cost = P(1-m)
   is never needed; the post-change cost is given as an absolute replacement value.)

2. Is the margin a ratio or a percent?  Text says "ratio is 0.3" with no percent word -> plain ratio, used as-is.
   Robustness: if an instance ever phrases it as "30 percent" / "30%", the parser divides by 100.

3. "discounted by 0.2 of the original price": discount AMOUNT = d * P (price falls BY that amount, not TO d*P).
   New price P1 = P * (1 - d).  "by ... of the original price" rules out an absolute USD discount and rules out
   "discounted to".  Robustness: "discounted by 20 percent" also handled; "discounted by X USD" treated as absolute.

4. "post-change unit cost is 61 USD": an absolute new cost C, not an increment on the baseline cost (no "increase",
   "rises by", "additional" wording).  Post-change unit gross profit GP1 = P1 - C.

5. What does "percentage ... retained" mean?  (a) GP1 / GP0 * 100  vs  (b) (GP1 - GP0) / GP0 * 100 (a change).
   Text: "a result above 100 percent means the post-change unit gross profit exceeds the baseline" -> (a), the plain
   ratio of post-change to baseline, times 100.  It is explicitly NOT the post-change gross-margin percentage
   (GP1 / P1), so that distractor is excluded.

6. Sign / floor: nothing in the text floors the result at zero or caps it; a negative GP1 would give a negative
   retention and >100 is explicitly allowed.  No clamping applied.

7. Rounding: "Use exact arithmetic without feeding the independently displayed checkpoint downstream" -> P1 is kept
   exact (not rounded to 4 dp) when computing GP1.  Everything is returned unrounded; the framework rounds.

8. Units: final is "percent" (71.1 means 71.1%), so multiply the ratio by 100.  Slot is "usd": P1 itself.

9. Checkpoint identity: "discounted selling price per unit before subtracting unit cost" = P1 = P * (1 - d),
   NOT the discount amount d*P and NOT the post-change gross profit.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h057"


def _grab_rate(patterns: list[str], text: str) -> Fraction:
    """Return a rate as a plain ratio.  Each pattern must contain {N}; if the matched number is immediately
    followed by 'percent' / '%' the value is divided by 100, otherwise it is used as a ratio."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})") + r"(\s*(?:percent|per cent|%))?"
        m = re.search(rx, text, flags=re.S | re.I)
        if m is not None:
            value = F(m.group(1))
            if m.group(2):
                value = value / 100
            return value
    raise ValueError(f"none of the rate patterns matched: {patterns!r}")


def _grab_money(patterns: list[str], text: str) -> Fraction:
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is not None:
            return F(m.group(1))
    raise ValueError(f"none of the money patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    # Original (undiscounted) unit price P, USD.
    price = _grab_money(
        [
            r"original unit price is (?:USD\s*)?{N}",
            r"original (?:selling |unit )?price (?:of|is) (?:USD\s*)?{N}",
        ],
        text,
    )

    # Baseline gross margin ratio m, computed on the undiscounted price P  (ambiguities 1-2).
    margin = _grab_rate(
        [
            r"baseline gross margin ratio is {N}",
            r"baseline gross margin (?:ratio|percentage|rate)?\s*(?:is|of) {N}",
            r"gross margin (?:ratio|percentage|rate)?\s*(?:is|of) {N}",
        ],
        text,
    )

    # Price discount d as a fraction of the original price  (ambiguity 3).
    m_abs = re.search(r"discounted by (?:USD\s*)?(" + NUMBER + r")\s*USD", text, flags=re.I)
    if m_abs is not None:
        # Absolute USD discount (not the wording in any seen instance, kept for robustness).
        discount_amount = F(m_abs.group(1))
    else:
        discount = _grab_rate(
            [
                r"discounted by {N}(?=\s*(?:of|percent|per cent|%))",
                r"discount(?:ed)? (?:of|by) {N}",
            ],
            text,
        )
        discount_amount = price * discount

    # Post-change unit cost C, USD (absolute replacement value, ambiguity 4).
    cost_new = _grab_money(
        [
            r"post-change unit cost is (?:USD\s*)?{N}",
            r"(?:new|post-change|revised) (?:per-)?unit cost (?:is|of) (?:USD\s*)?{N}",
        ],
        text,
    )

    # --- computation, all exact Fractions ---
    gp_baseline = margin * price                 # original per-unit gross profit
    price_discounted = price - discount_amount    # checkpoint: discounted selling price per unit (exact, unrounded)
    gp_new = price_discounted - cost_new          # post-change per-unit gross profit
    retention_pct = gp_new / gp_baseline * 100    # ambiguity 5: plain ratio x 100, no clamping (ambiguity 6)

    return {
        "final": retention_pct,
        "slots": {"discounted_unit_price_checkpoint": price_discounted},
    }
