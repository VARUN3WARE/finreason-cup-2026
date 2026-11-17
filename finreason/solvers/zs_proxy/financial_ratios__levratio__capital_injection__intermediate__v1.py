from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.levratio.capital_injection.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    liab = grab(r"[Tt]otal liabilities are {N} USD", text)
    eq0 = grab(r"total equity before an owner capital injection is {N} USD", text)
    inj = grab(r"injection adds {N} USD to equity", text)
    eq1 = eq0 + inj
    return {"final": Fraction(liab) / eq1, "slots": {"trace_1": eq1}}
