from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.deal_structure.stock_swap_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    stock = grab(r"Stock consideration is {N} USD", text)
    per_share = grab(r"value per issued share is {N} USD per share", text)
    return {"final": stock / per_share, "slots": {}}
