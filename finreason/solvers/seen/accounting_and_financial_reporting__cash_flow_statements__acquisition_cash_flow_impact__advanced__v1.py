from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.acquisition_cash_flow_impact.advanced.v1"


def solve(text: str, q: dict) -> dict:
    payment = grab(r"upfront cash payment of {N}", text)
    operating = grab(r"operating savings {N}", text)
    tax = grab(r"tax savings {N}", text)
    revenue = grab(r"additional revenue cash contribution {N}", text)
    wc = grab(r"working-capital benefits {N}", text)
    tech = grab(r"technology integration {N}", text)
    workforce = grab(r"workforce integration {N}", text)
    synergies = operating + tax + revenue + wc
    costs = payment + tech + workforce
    return {"final": Fraction(synergies - costs), "slots": {"trace_1": synergies, "trace_2": costs}}
