from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.global_events_impact.crypto_volume_increase.basic.v1"


def solve(text: str, q: dict) -> dict:
    v0 = grab(r"initial volume is {N} USD", text)
    inc = grab(r"increase is {N} percent", text) / 100
    mult = 1 + inc
    return {"final": v0 * mult, "slots": {"volume_multiple_trace": mult}}
