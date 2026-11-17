from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_working_capital.basic.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"Current assets are {N}", text)
    cl = grab(r"current liabilities are {N}", text)
    # Plain difference; no floor (inputs are disclosed to give CA >= CL).
    return {"final": ca - cl, "slots": {}}
