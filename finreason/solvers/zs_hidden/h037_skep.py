"""Solver for hidden cluster h037 -- minimum aggregate coupon cash for a target holding-period return.

Structure (all three instances share it):
    P  = quoted clean price                  ("quoted clean price P")
    R  = redemption cash over the holding period
    S  = settlement cost                     (ALL acquisition cash beyond the clean quote: accrued
                                              interest + fees already inside S -- "do not add those again")
    O  = total acquisition outlay = P + S    (checkpoint: "clean price plus all additional acquisition cash")
    HPR(C) = (C + R - O) / O                 (C = aggregate coupon cash)
    target: HPR(C) = t exactly  ->  C = O * (1 + t) - R

AMBIGUITIES CONSIDERED AND RESOLUTIONS
1. Is the target a percent or a ratio?  Text: "target return ratio 0.05" -> plain ratio; use as-is, no /100.
   (0.5 and 0.4 in the other instances would be absurd as percents of a bond return anyway.)
2. Does settlement cost get accrued interest / fees added on top?  No: S is "defined as all acquisition
   cash beyond the clean quote, including accrued interest and fees ...; do not add those amounts again."
   So O = P + S and nothing else (S may be 0).
3. Which denominator does the return use?  Text: "... divided by total acquisition outlay" -> O, not the
   clean price P.
4. "Minimum ... that exactly meets": HPR is strictly increasing in C, so the smallest C with HPR >= t is
   the C with HPR == t, i.e. the unique root of the linear equation.  No floor at zero is applied
   because the text asks for the value that *exactly* meets the target (and in all three instances the
   root is positive anyway, so a zero floor would not change the output).
5. Rounding: "use exact arithmetic through all intermediate steps, round only the final value" -> return
   unrounded Fractions; the framework renders half-up to 2 dp.  Nothing in the text uses a rounded value
   downstream.
6. Checkpoint "acquisition_outlay_checkpoint": "clean price plus all additional acquisition cash" = P + S
   (in USD).  It is independently rounded by the framework; the unrounded value feeds the final answer.
7. Units: all cash amounts are in USD; answer unit "usd" -> return C in the same cash units as the inputs.
8. Number parsing: anchored on the distinct phrases "quoted clean price", "redemption cash",
   "settlement cost", "target return ratio" so that the numbers cannot be confused with each other.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h037"


def solve(text: str, q: dict) -> dict:
    clean_price = grab(r"quoted clean price\s+{N}", text)
    redemption = grab(r"redemption cash\s+{N}", text)
    settlement = grab(r"settlement cost\s+{N}", text)
    target = grab(r"target return ratio\s+{N}", text)  # already a ratio (not a percent)

    # Total acquisition outlay: clean price plus all additional acquisition cash (settlement cost
    # already contains accrued interest and fees -- nothing else is added).
    outlay = clean_price + settlement

    # HPR = (C + R - O) / O = t  ->  C = O * (1 + t) - R   (exact rational arithmetic)
    coupon_cash = outlay * (Fraction(1) + target) - redemption

    return {
        "final": coupon_cash,
        "slots": {
            "acquisition_outlay_checkpoint": outlay,
        },
    }
