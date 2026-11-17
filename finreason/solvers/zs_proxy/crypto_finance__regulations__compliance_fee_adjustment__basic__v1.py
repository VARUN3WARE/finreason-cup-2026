from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.regulations.compliance_fee_adjustment.basic.v1"


def solve(text: str, q: dict) -> dict:
    fee = grab(r"compliance fee of {N} USD", text)
    mult = grab(r"adjustment multiple of {N}", text)
    return {"final": fee * mult, "slots": {}}
