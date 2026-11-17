"""h006 -- inverse single-factor stress test with partial exposure.

Text structure (all 3 instances):
  "A portfolio is worth V, but only share w is exposed to one factor. The exposed
   portion has signed sensitivity s. Determine the signed factor shock required to
   produce target portfolio value change dV, and report that shock as a percentage."

Checkpoint exposed_value_checkpoint (usd, half_up 2dp): "the factor-exposed portfolio value".
Final (percent, half_up 2dp): the signed factor shock in percent.

AMBIGUITY HUNT -- points where analysts could disagree, and the resolution used:

A1. Is "share 0.5" a ratio or a percent?
    -> Ratio. No "percent" word accompanies it, and a share of 0.5% of a 196 USD
       portfolio (0.98 USD exposed) would be an absurd reading of "share". The
       checkpoint unit is usd, so exposed value = V * w = 98 for V=196, w=0.5.

A2. Does the sensitivity apply to the whole portfolio or only to the exposed part?
    -> Only to the exposed portion: "only share w is exposed to one factor. The
       exposed portion has signed sensitivity s." The unexposed part has zero factor
       sensitivity, so total change dV = (V*w) * (shock/100) * s.

A3. Percent vs ratio for the shock.
    -> The dataset's seen single-factor templates define impact = V*(c/100)*s with c in
       percent. The question explicitly says "report that shock as a percentage" and the
       answer unit is `percent`, so shock_pct = 100 * dV / (V * w * s). The value returned
       is the percent number (e.g. -209.18 means -209.18%), unrounded.

A4. Sign handling.
    -> Everything is "signed": keep the sign of dV and s through the division; no abs(),
       no floor at zero. A negative target with positive s gives a negative shock; a
       negative s flips the sign.

A5. Is the exposed-value checkpoint V*w or V*w*s (sensitivity-weighted exposure)?
    -> V*w. The slot says "factor-exposed portfolio value" in usd, i.e. the dollar amount
       of the portfolio exposed to the factor, before any sensitivity scaling.

A6. Rounding.
    -> No intermediate rounding anywhere ("use exact arithmetic through all intermediate
       steps"); both the slot and the final are returned as exact Fractions and the
       framework applies half-up 2dp rendering independently.

A7. Degenerate inputs.
    -> If V*w*s == 0 the shock is undefined; raise rather than guess. Not hit by any
       of the 3 instances.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h006"


def solve(text: str, q: dict) -> dict:
    # Inputs, anchored on surrounding words.
    value = grab(r"portfolio is worth {N}", text)                          # V, usd
    share = grab(r"only share {N} is exposed", text)                       # w, ratio (A1)
    sens = grab(r"signed sensitivity {N}", text)                           # s, dimensionless
    target = grab(r"target portfolio value change {N}", text)             # dV, usd (signed)

    # Checkpoint: dollar value of the portfolio exposed to the factor (A5).
    exposed_value = value * share

    # dV = exposed_value * (shock_pct / 100) * s  ->  shock_pct = 100 * dV / (exposed_value * s)   (A2, A3, A4)
    denom = exposed_value * sens
    if denom == 0:
        raise ValueError("factor shock undefined: exposed value times sensitivity is zero")
    shock_pct = Fraction(100) * target / denom

    return {
        "final": shock_pct,
        "slots": {"exposed_value_checkpoint": exposed_value},
    }
