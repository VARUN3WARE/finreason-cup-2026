# =====================================================================================
# h112 -- DeFi liquidity position with an optional, threshold-triggered impermanent-loss hedge
# =====================================================================================
#
# FINANCE MODEL (standard conventions; every override is noted)
# -------------------------------------------------------------
# One common annual period; every ratio below is a fraction of the position's STARTING CAPITAL C
# (USD).  No compounding, no annualisation, no time value (one period, "common" to all flows).
#
#   fees            = f  * C        f  = "fee-yield ratio"   (LP fee income over the period)
#   unhedged loss L = il * C        il = "impermanent-loss ratio" (loss of the LP position vs
#                                        simply holding the two assets, as a ratio of capital)
#                                   L is the USD size of the loss the hedge is able to cover.
#   hedge coverage c                the hedge covers the fraction c of THAT loss, i.e. it pays
#                                   out / offsets  c * L  of the impermanent loss
#   covered-loss ratio  = c * il    "covered impermanent loss as a ratio of position capital"
#                                   (a property of the hedge terms; it is the candidate hedge
#                                   offset per unit of capital, computed BEFORE the activation
#                                   decision, so it is independent of which branch is selected --
#                                   this matches how every conditional template in this task
#                                   family reports its checkpoint: as the pre-selection candidate)
#   hedge cost  h * C               h = cost ratio of capital; paid ONLY when the hedge is
#                                   activated (explicit override of "always pay a premium")
#
#   Activation rule (explicit): activate  <=>  L  >  risk limit R   (STRICT inequality, EXACT
#   unrounded L in USD; equality => NOT activated => unhedged, no hedge cost).
#
#   Net result (profit if positive, loss if negative) in USD, "excluding return of the original
#   capital" (so we report P&L only, never C itself):
#       unhedged :  net_U = fees - L                       = C * (f - il)
#       hedged   :  net_H = fees - L + c*L - h*C           = C * (f - (1 - c)*il - h)
#   selected net = net_H if activated else net_U      (the rule SELECTS; it does not take the max)
#
# HOW EACH GIVEN NUMBER ENTERS
#   capital C        -> scales fees, L, covered loss, hedge cost
#   fee-yield f      -> fee income f*C (always earned, both branches)
#   IL ratio il      -> loss L = il*C (always incurred, both branches); drives the trigger test
#   coverage c       -> offset c*L, only in the hedged branch; also the checkpoint c*il
#   hedge cost h     -> h*C, only in the hedged branch
#   risk limit R     -> compared with the exact L in USD, strictly
#
# ROUNDING
#   Everything is exact (Fraction).  Nothing is rounded inside the computation: the trigger test
#   uses the exact L, and the framework rounds the final net half-up to 2 dp and the covered-loss
#   checkpoint half-up to 6 dp from the unrounded values returned here.
#
# CHECKPOINT
#   covered_loss_ratio_checkpoint (unit: ratio)  = c * il   (plain ratio, e.g. 0.12 not 12 percent)
# =====================================================================================

from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401  (exact number parsing helpers)

TEMPLATE_ID = "h112"


def solve(text: str, q: dict) -> dict:
    # ---- parse (anchored on the surrounding words, never on instance values) -------------
    capital = grab(r"has capital of {N} USD", text)                    # C
    fee_yield = grab(r"fee-yield ratio {N}", text)                     # f
    il_ratio = grab(r"impermanent-loss ratio {N}", text)               # il
    coverage = grab(r"hedge covers {N} of that loss", text)            # c
    hedge_cost_ratio = grab(r"costs {N} of capital", text)             # h
    risk_limit = grab(r"risk limit of {N} USD", text)                  # R

    # ---- the model -----------------------------------------------------------------------
    fees = capital * fee_yield                                         # USD fee income
    unhedged_loss = capital * il_ratio                                 # USD impermanent loss L
    covered_loss_ratio = coverage * il_ratio                           # checkpoint (ratio of capital)
    covered_loss = capital * covered_loss_ratio                        # USD offset if hedged (= c*L)
    hedge_cost = capital * hedge_cost_ratio                            # USD premium, only if hedged

    net_unhedged = fees - unhedged_loss
    net_hedged = fees - unhedged_loss + covered_loss - hedge_cost

    activate = unhedged_loss > risk_limit                              # strictly exceeds, exact
    net = net_hedged if activate else net_unhedged

    return {
        "final": Fraction(net),
        "slots": {"covered_loss_ratio_checkpoint": Fraction(covered_loss_ratio)},
    }
