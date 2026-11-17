from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_pe_valuation.basic.v1"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is {N}", text)
    pe = grab(r"multiple is {N} times", text)
    return {"final": ni * pe, "slots": {}}
