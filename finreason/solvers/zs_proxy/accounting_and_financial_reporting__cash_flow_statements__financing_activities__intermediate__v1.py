from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.financing_activities.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    equity = grab(r"issuing equity (?:are|is|of)\s+(?:USD\s+)?{N}", text)
    debt = grab(r"issuing debt (?:are|is|of)\s+(?:USD\s+)?{N}", text)
    repay = grab(r"Debt repayments (?:are|is|of)\s+(?:USD\s+)?{N}", text)
    divs = grab(r"dividends paid (?:are|is|of)\s+(?:USD\s+)?{N}", text)
    inflows = equity + debt
    # Repayments and dividends are given as positive outflow magnitudes.
    outflows = repay + divs
    return {"final": inflows - outflows, "slots": {"trace_1": inflows, "trace_2": outflows}}
