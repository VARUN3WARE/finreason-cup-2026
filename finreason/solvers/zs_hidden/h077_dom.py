# FINANCE MODEL (h077): minimum opening cash under two period-end liquidity floors.
#
#   O      = unknown opening cash (carried into period one)
#   in1/out1, in2/out2 = stated inflows / outflows of period one / two (USD millions)
#   net1   = in1 - out1          (period-one net cash flow)
#   net2   = in2 - out2          (period-two net cash flow)
#   floor  = required minimum period-end cash balance, applied to EACH period end
#
#   End of period one cash:  C1 = O + net1            -> need C1 >= floor  => O >= floor - net1
#   End of period two cash:  C2 = O + net1 + net2     -> need C2 >= floor  => O >= floor - net1 - net2
#
#   Both must hold, so the minimum opening cash is the larger (binding) lower bound:
#       O_min = max(floor - net1, floor - net1 - net2)
#   Which period binds depends on the sign of net2 (net2 < 0 -> period two binds, else period one).
#
# Conventions / overrides noted from the text:
#   - Only period-end balances are tested (no intraperiod minima), no interest, no other flows.
#   - Opening cash is the single unknown carried through both periods; no non-negativity restriction
#     is stated, and every floor here is positive, so the bound is never below zero in practice.
#   - Final answer in USD millions, returned unrounded (framework rounds half-up to 2 dp).
#   - Checkpoint: period-one net cash flow divided by the required cash floor (plain ratio,
#     unrounded; framework rounds half-up to 6 dp).
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h077"


def solve(text: str, q: dict) -> dict:
    in1, out1 = grab_all(r"Period one has cash inflow {N} and cash outflow {N}", text)
    in2, out2 = grab_all(r"Period two then has cash inflow {N} and cash outflow {N}", text)
    floor = grab(r"balance must be at least {N}", text)

    net1 = in1 - out1
    net2 = in2 - out2

    bound_p1 = floor - net1                # opening cash needed so period-one end >= floor
    bound_p2 = floor - net1 - net2         # opening cash needed so period-two end >= floor
    opening = max(bound_p1, bound_p2)

    return {
        "final": opening,
        "slots": {
            "period_one_net_to_floor_ratio_checkpoint": net1 / floor,
        },
    }
