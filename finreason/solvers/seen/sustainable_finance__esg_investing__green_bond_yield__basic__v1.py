from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.green_bond_yield.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"principal\s+{N}\s+USD", text)
    yld = grab(r"annual yield is\s+{N}\s+percent", text) / 100
    years = grab(r"\bfor\s+{N}\s+years?\b", text)
    annual = principal * yld
    return {"final": annual * years, "slots": {"annual_interest_trace": annual}}
