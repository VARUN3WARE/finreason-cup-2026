from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h037"


def solve(text: str, q: dict) -> dict:
    clean = grab(r"quoted clean price {N}", text)
    redemption = grab(r"redemption cash {N}", text)
    settle = grab(r"settlement cost {N}", text)
    target = grab(r"target return ratio {N}", text)

    # settlement cost already includes accrued interest and fees -- not added again
    outlay = clean + settle
    # (C + R - O) / O = target  ->  C = O * (1 + target) - R
    coupon = outlay * (1 + target) - redemption
    # coupon cash cannot be negative; the minimum meeting the target is floored at zero
    if coupon < 0:
        coupon = Fraction(0)
    return {"final": coupon, "slots": {"acquisition_outlay_checkpoint": outlay}}
