from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.cross_border_net.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    notional = grab(r"notional amount of {N} USD", text)
    conv = grab(r"conversion multiple is {N}", text)
    spread_pct = grab(r"platform spread is {N} percent", text)
    fixed_fee = grab(r"fixed processing fee is {N} USD", text)
    spread = spread_pct / 100
    platform_multiple = conv * (1 - spread)
    before_fee = notional * platform_multiple
    net = before_fee - fixed_fee
    return {
        "final": net,
        "slots": {
            "platform_multiple_trace": platform_multiple,
            "before_fee_trace": before_fee,
        },
    }
