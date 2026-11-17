from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.financing_activities.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    equity = grab(r"issuing equity are {N}", text)
    debt = grab(r"issuing debt are {N}", text)
    repay = grab(r"[Dd]ebt repayments are {N}", text)
    divs = grab(r"dividends paid are {N}", text)
    # Repayments and dividends are given as positive outflow magnitudes.
    inflows = equity + debt
    outflows = repay + divs
    return {"final": Fraction(inflows - outflows), "slots": {"trace_1": inflows, "trace_2": outflows}}
