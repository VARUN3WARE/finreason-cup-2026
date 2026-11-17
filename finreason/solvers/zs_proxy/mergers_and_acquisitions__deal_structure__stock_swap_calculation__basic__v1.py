from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.deal_structure.stock_swap_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    consideration = grab(r"[Ss]tock consideration is {N} USD", text)
    share_value = grab(r"value per issued share is {N} USD", text)
    shares = consideration / share_value
    return {"final": shares, "slots": {}}
