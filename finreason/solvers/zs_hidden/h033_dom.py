# FINANCE MODEL
# -------------
# A token supply U (units) trades at current price P (USD). Price is stressed in exactly
# three sequential stages; each stage removes the same ratio d of the price that survived the
# previous stage (no replenishment), so the one-stage retention ratio is k = 1 - d and the
# three-stage stressed price is  Ps = P * k^3  (integer power, exact Fraction arithmetic).
#
# Burn policy:     supply U_b = U - burned units; treasury support lifts the stressed price ONCE
#                  by ratio s:  P_b = Ps * (1 + s);   market cap MC_b = U_b * P_b.
# Emission policy: supply U_e = U + emitted units; no support: P_e = Ps;  MC_e = U_e * Ps.
# Selection: burn if MC_b >= floor (at least -> inclusive, tested on the exact value), else emission.
# Final answer = selected market cap in USD (half-up to 2 dp applied by the framework).
# Checkpoint "one_stage_price_retention_checkpoint" = 1 - d (ratio, plain number, 6 dp half-up).
# No overrides of standard conventions; no intermediate rounding (all exact Fractions).

import re
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h033"


def solve(text: str, q: dict) -> dict:
    units = grab(r"A token has {N} units", text)
    price = grab(r"current price of {N} USD", text)
    d = grab(r"the same ratio {N} is removed", text)
    burned = grab(r"Under the burn policy, {N} units are removed", text)
    support = grab(r"raises that stressed price once by ratio {N}", text)
    emitted = grab(r"emission policy, {N} units are added", text)
    floor = grab(r"resulting market cap is at least {N} USD", text)

    n_stages = 3  # "exactly three sequential stress stages"
    retention = 1 - d
    stressed = price * retention ** n_stages

    mc_burn = (units - burned) * stressed * (1 + support)
    mc_emit = (units + emitted) * stressed

    final = mc_burn if mc_burn >= floor else mc_emit

    return {
        "final": final,
        "slots": {"one_stage_price_retention_checkpoint": retention},
    }
