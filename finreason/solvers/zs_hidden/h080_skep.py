"""h080 -- two-player Shapley attribution of procurement savings (skeptical / ambiguity-hunting pass).

Structure (identical in all 3 instances, numbers differ):
    P  = procurement program alone  (USD millions)
    I  = IT program alone           (USD millions)
    B  = both programs together     (USD millions)
    "Attribute procurement savings by giving equal weight to its marginal contribution in both
     possible implementation orders": first  -> P - v(empty) = P ; after IT -> B - I.
    attribution = (P + (B - I)) / 2
    final       = attribution / B * 100         (percent of COMBINED-program savings)

AMBIGUITIES HUNTED AND RESOLVED
1. Checkpoint quantity. Slot "procurement_marginal_after_it_checkpoint" = "procurement marginal savings
   when procurement follows IT". Text: "combined-program savings minus IT-only savings when introduced
   after IT". So the checkpoint is the RAW marginal B - I, NOT the half-weighted term (B - I)/2 and NOT
   the final attribution. Unit usd_million -> no scaling; inputs are already in USD millions.
2. "Equal weight" -> 1/2 and 1/2 (two orders, two-player Shapley). Not a 50/50 split of B, not weights
   proportional to standalone sizes.
3. Marginal contribution "when introduced first" = procurement-only savings P (v(empty)=0, confirmed by
   the text calling it "its procurement-only savings when introduced first"). Nothing is subtracted.
4. Denominator of the percentage: "What percentage of combined-program savings" -> divide by B, not by
   P + I and not by the attribution of both programs (those two coincide anyway: Shapley sums to B).
5. Unit of final = percent -> ratio * 100 (e.g. 54.85, not 0.5485).
6. Rounding: nothing in the text says a rounded value is reused downstream; everything exact, framework
   rounds (final 2 dp half-up, checkpoint 4 dp half-up).
7. Sentence "combined result is strictly greater than either standalone result but strictly less than
   their sum" and "No program delivers zero savings" are consistency GUARANTEES, not branches; no floor
   at zero, no max/min, no sign flip. Implemented as a non-fatal sanity note only (never alters values).
8. Parsing anchored on the program labels ("procurement program alone would deliver", "IT program alone
   would deliver", "implementing both would deliver"), not on number order; commas/decimals/rationals are
   handled by finreason.nums. Whitespace is matched with \\s+ in case of double spaces.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h080"


def _grab_first(patterns: list[str], text: str) -> Fraction:
    """Try several anchored patterns in order; return the first that matches."""
    last_err: Exception | None = None
    for pat in patterns:
        try:
            return grab(pat, text)
        except ValueError as exc:  # pattern not found -> try next
            last_err = exc
    raise ValueError(f"none of the patterns matched: {patterns}") from last_err


def solve(text: str, q: dict) -> dict:
    t = re.sub(r"\s+", " ", text)

    # P: procurement program alone
    P = _grab_first(
        [
            r"procurement\s+program\s+alone\s+would\s+deliver\s+(?:about\s+|approximately\s+|roughly\s+)?{N}",
            r"procurement\s+program\s+alone[^.;,]*?{N}\s*USD\s+millions?",
            r"procurement[^.;,]*?alone[^.;,]*?{N}",
        ],
        t,
    )
    # I: IT program alone
    I = _grab_first(
        [
            r"IT\s+program\s+alone\s+would\s+deliver\s+(?:about\s+|approximately\s+|roughly\s+)?{N}",
            r"IT\s+program\s+alone[^.;,]*?{N}\s*USD\s+millions?",
            r"\bIT\b[^.;,]*?alone[^.;,]*?{N}",
        ],
        t,
    )
    # B: both programs together
    B = _grab_first(
        [
            r"implementing\s+both\s+would\s+deliver\s+(?:about\s+|approximately\s+|roughly\s+)?{N}",
            r"both\s+(?:programs\s+)?would\s+deliver\s+(?:about\s+|approximately\s+|roughly\s+)?{N}",
            r"both[^.;,]*?{N}\s*USD\s+millions?",
        ],
        t,
    )

    # Consistency guarantees stated in the text (never branch on them, never alter values).
    # B > max(P, I) and B < P + I ; P, I != 0.
    _consistent = (B > P and B > I and B < P + I and P != 0 and I != 0)  # noqa: F841

    # Checkpoint: procurement's marginal contribution when it follows IT (raw, unweighted, USD millions).
    marginal_after_it = B - I

    # Marginal when introduced first is just the standalone procurement savings.
    marginal_first = P

    # Equal-weight (Shapley) attribution to procurement, in USD millions.
    attribution = Fraction(1, 2) * marginal_first + Fraction(1, 2) * marginal_after_it

    # Percentage of combined-program savings attributed to procurement.
    final_pct = attribution / B * 100

    return {
        "final": final_pct,
        "slots": {"procurement_marginal_after_it_checkpoint": marginal_after_it},
    }
