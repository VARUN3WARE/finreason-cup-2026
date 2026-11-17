"""Hidden cluster h004 -- stress-loss net reserve after recoveries.

Question structure (3 instances, numbers differ):
    "A portfolio worth V faces market shock ratio S with loss sensitivity B, plus liquidity
     shock ratio L applied directly to portfolio value. The institution expects to recover
     ratio R of the combined gross loss. Compute the net reserve required after subtracting
     the recoverable amount from gross stress loss."
Checkpoint market_loss_checkpoint: "Report the market stress dollar loss" (usd, half-up 2dp).
Final: net reserve (usd, half-up 2dp).

AMBIGUITIES CONSIDERED AND RESOLUTIONS
--------------------------------------
A1. Market loss = V * S * B (shock ratio times loss sensitivity times portfolio value) rather
    than V * S alone.  Evidence: the liquidity shock is described as "applied DIRECTLY to
    portfolio value", a deliberate contrast with the market shock, which is mediated by the
    stated "loss sensitivity".  A sensitivity that was not applied would have no role in the
    question, so market loss = V * S * B.
A2. Liquidity loss base = the ORIGINAL portfolio value V, not the post-market-shock value
    (V - market loss).  Evidence: "applied directly to portfolio value" (no sequencing words
    such as "remaining" / "after the market shock").  Liquidity loss = V * L.
A3. Gross stress loss = market loss + liquidity loss ("the combined gross loss").
A4. Recoverable amount = R * gross loss.  Evidence: "recover ratio R of the combined gross
    loss" -- the base is explicitly the combined gross loss, not the market loss alone.
A5. Net reserve = gross loss - recoverable (literal "after subtracting the recoverable
    amount from gross stress loss").  No floor at zero is stated, so none is applied; for
    R in [0, 1] (all three instances: 0, 1, 0.24875) the result is non-negative anyway.
    R = 1 legitimately yields a 0.00 reserve; R = 0 yields the full gross loss.
A6. Units: every input described as a "ratio" is a plain ratio (0.2 means 20%), not a
    percent number -- no /100.  "worth 98" is in USD, matching the usd answer unit.
A7. No rounding anywhere inside the chain (text: exact arithmetic through all intermediate
    steps); both the checkpoint and the final are returned unrounded for the framework.
A8. Checkpoint "market stress dollar loss" is the market-shock component only (V * S * B),
    in USD -- not the gross loss and not the liquidity component.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h004"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth {N}", text)
    market_shock = grab(r"market shock ratio {N}", text)
    sensitivity = grab(r"loss sensitivity {N}", text)
    liquidity_shock = grab(r"liquidity shock ratio {N}", text)
    recovery = grab(r"recover ratio {N}", text)

    # A1/A8: market stress dollar loss, mediated by the loss sensitivity.
    market_loss = value * market_shock * sensitivity
    # A2: liquidity shock applied directly to (original) portfolio value.
    liquidity_loss = value * liquidity_shock
    # A3: combined gross stress loss.
    gross_loss = market_loss + liquidity_loss
    # A4: recoverable amount is a ratio of the combined gross loss.
    recoverable = recovery * gross_loss
    # A5: net reserve = gross - recoverable (no floor stated).
    net_reserve = gross_loss - recoverable

    return {
        "final": net_reserve,
        "slots": {"market_loss_checkpoint": market_loss},
    }
