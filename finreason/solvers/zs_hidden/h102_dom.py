# h102 -- "additional stake in a second DeFi pool to reach a target NET annual reward" (domain lens)
#
# ---------------------------------------------------------------------------------------------
# FINANCE MODEL (written before coding)
# ---------------------------------------------------------------------------------------------
# Horizon: exactly ONE annual period.  A "yield ratio" r is the simple annual yield per unit of
# principal, so a position of principal P earns  P * r  USD over the year.  No compounding, no
# time-scaling, no percent conversion (a ratio such as 0.1 or 1/7 is already a plain fraction).
#
# Positions
#   existing position : principal P1 (USD), yield ratio r1  -> gross reward R1 = P1 * r1
#   second pool       : added principal x (USD, UNKNOWN), yield ratio r2 -> gross reward R2 = x * r2
#
# Fee
#   The protocol charges a FIXED annual fee F (USD).  It "does not depend on the added principal",
#   i.e. it is a constant that is subtracted once from the user's total reward and is the same
#   whatever x is (so it is NOT a rate applied to x, and it does not shrink the yield ratio r2).
#
# Net annual reward (the quantity the question asks to "deliver", target T in USD)
#   Net(x) = R1 + R2 - F = P1*r1 + x*r2 - F          (total over both pools, after the fixed fee)
#
# Required additional stake: solve Net(x) = T for x.  Net is linear and strictly increasing in x
# (r2 > 0), so the solution is unique and closed-form:
#       gross reward needed overall   G  = T + F
#       reward still missing           S  = G - R1  = T + F - P1*r1     (what the second pool must supply)
#       additional principal           x  = S / r2
#   Units: R1, F, T, S in USD; r1, r2 are dimensionless ratios; x in USD.
#
# Checkpoint (slot 1 "existing_reward_checkpoint"): "the reward supplied by the existing position"
#   = the existing position's gross annual reward R1 = P1 * r1 (USD), BEFORE the fee (the fee is a
#   protocol-level charge on the whole account; the existing position by itself "supplies" P1*r1
#   of the gross reward that has to reach T + F).  Exact, unrounded; the framework rounds it to 4 dp.
#
# Overrides of standard conventions: none.  Everything is exact Fraction arithmetic, with no
# intermediate rounding (the text says: round only the final value, half up, to 2 dp; the
# checkpoint is rounded independently by the framework).
#
# Edge handling: "additional stake required" cannot be negative.  If the existing position alone
# already delivers Net >= T (S <= 0) the required additional stake is 0.  This guard is NOT binding
# for any of the three instances (S > 0 in each), it only makes the function total.
# ---------------------------------------------------------------------------------------------
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h102"


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on the surrounding words, never on instance values) -------------------
    p1, r1 = grab_all(r"already has {N} USD earning yield ratio {N}", text)
    r2 = grab(r"second pool offers yield ratio {N}", text)
    fee = grab(r"fixed annual fee of {N} USD", text)
    target = grab(r"net annual reward of {N} USD", text)

    # --- model ---------------------------------------------------------------------------------
    existing_reward = p1 * r1                      # R1 = P1 * r1   (USD, gross, one annual period)
    gross_needed = target + fee                    # G  = T + F     (fixed fee is paid once, regardless of x)
    shortfall = gross_needed - existing_reward     # S  = G - R1    (must come from the second pool)
    if shortfall < 0:
        shortfall = Fraction(0)                    # target already met -> nothing to add (not binding here)
    added_stake = shortfall / r2                   # x  = S / r2

    return {
        "final": added_stake,
        "slots": {"existing_reward_checkpoint": existing_reward},
    }
