from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h011"


def solve(text: str, q: dict) -> dict:
    direct = grab(r"has {N} direct long shares", text)
    attributed = grab(r"{N} shares attributed through related holdings", text)
    notional = grab(r"derivative notional equivalent to {N} shares", text)
    delta = grab(r"exposure delta {N}", text)
    short = grab(r"{N} shares of offsetting short exposure", text)
    outstanding = grab(r"issuer has {N} shares outstanding", text)

    deriv_eq = notional * delta
    net = direct + attributed + deriv_eq - short  # signed, no floor
    pct = net / outstanding * 100
    return {"final": Fraction(pct), "slots": {"derivative_equivalent_checkpoint": Fraction(deriv_eq)}}
