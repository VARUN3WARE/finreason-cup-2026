from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.capital_structure.debt_to_equity_aggregate_debt.basic.v1"


def solve(text: str, q: dict) -> dict:
    st = grab(r"[Ss]hort-term debt is {N} USD million", text)
    lt = grab(r"[Ll]ong-term debt is {N} USD million", text)
    equity = grab(r"equity is {N} USD million", text)
    total = st + lt
    return {"final": total / equity, "slots": {"trace_1": total}}
