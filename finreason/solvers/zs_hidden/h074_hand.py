from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h074"


def solve(text: str, q: dict) -> dict:
    share = grab(r"green tranche receives share {N}", text)
    rg = grab(r"green tranche receives share [^,]*, earns annual yield ratio {N}", text)
    ng = grab(r"green tranche receives share .*?compounds for {N} annual periods", text)
    rc = grab(r"conventional tranche, which earns annual yield ratio {N}", text)
    nc = grab(r"conventional tranche, which earns annual yield ratio [^,]*?and compounds for {N} annual periods", text)
    cap = grab(r"maturity-repayment cap {N}", text)

    if ng.denominator != 1 or nc.denominator != 1:
        raise ValueError("non-integer period count")
    green_factor = (1 + rg) ** int(ng)
    conv_factor = (1 + rc) ** int(nc)
    weighted = share * green_factor + (1 - share) * conv_factor
    principal = Fraction(cap) / weighted
    return {"final": principal, "slots": {"green_maturity_factor_checkpoint": green_factor}}
