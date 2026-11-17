# FINANCE MODEL (h037): required coupon cash for a target holding-period return on a bond.
#
#   P  = quoted clean price (USD)
#   S  = settlement cost = ALL acquisition cash beyond the clean quote (accrued interest + fees);
#        stated as already complete -> NOT added again anywhere else.
#   O  = total acquisition outlay = P + S                         (checkpoint 1, USD)
#   R  = redemption cash received over the holding period
#   C  = aggregate coupon cash received over the holding period (the unknown)
#   HPR = (C + R - O) / O        (explicit definition in the text; ratio, not percent)
#   target ratio g  (plain ratio, 0.05 means 5%)
#
#   "Minimum aggregate coupon cash that exactly meets target":  HPR is increasing in C, so the
#   minimum C that reaches HPR = g solves (C + R - O)/O = g  ->  C = O*(1+g) - R = g*O + (O - R).
#   Final answer = C in USD, half-up 2dp (framework rounds; we return the exact Fraction).
#
# Overrides / notes:
#   - No discounting, no annualisation: simple holding-period return as defined in the text.
#   - No floor at zero applied (C is the exact solution; all 3 instances give positive C anyway).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h037"


def solve(text: str, q: dict) -> dict:
    price = grab(r"quoted clean price {N}", text)
    redemption = grab(r"redemption cash {N}", text)
    settle = grab(r"settlement cost {N}", text)
    target = grab(r"target return ratio {N}", text)

    outlay = price + settle
    coupon = outlay * (1 + target) - redemption

    slots = {}
    for s in q["trace_spec"]["slots"]:
        sid = s["id"] if isinstance(s, dict) and "id" in s else s["slot_id"]
        slots[sid] = outlay
    return {"final": coupon, "slots": slots}
