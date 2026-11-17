from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.green_bond_yield.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"has principal {N} USD", text)
    y = grab(r"simple annual yield is {N} percent", text) / 100
    years = grab(r"inclusive with at most two decimal places, for {N} years", text)
    annual = principal * y
    total = annual * years
    return {"final": total, "slots": {"annual_interest_trace": annual}}
