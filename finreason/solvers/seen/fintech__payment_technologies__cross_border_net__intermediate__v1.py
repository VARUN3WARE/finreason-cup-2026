from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.cross_border_net.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    notional = grab(r"notional amount of {N} USD", text)
    mult = grab(r"conversion multiple is {N}", text)
    spread_pct = grab(r"platform spread is {N} percent", text)
    fee = grab(r"fixed processing fee is {N} USD", text)
    platform_mult = mult * (1 - spread_pct / 100)
    before_fee = notional * platform_mult
    net = before_fee - fee
    return {
        "final": net,
        "slots": {"platform_multiple_trace": platform_mult, "before_fee_trace": before_fee},
    }
