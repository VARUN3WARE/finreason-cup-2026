from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.acquisition_cash_flow_impact.advanced.v1"


def solve(text: str, q: dict) -> dict:
    payment = grab(r"upfront cash payment of\s+(?:USD\s+)?{N}", text)
    op = grab(r"operating savings\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    tax = grab(r"tax savings\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    rev = grab(r"additional revenue cash contribution\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    wc = grab(r"working-capital benefits\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    tech = grab(r"technology integration\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    work = grab(r"workforce integration\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    synergies = op + tax + rev + wc
    outlay = payment + tech + work
    return {"final": synergies - outlay, "slots": {"trace_1": synergies, "trace_2": outlay}}
