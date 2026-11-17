from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.valuation_methods.comp_ebitda_multiple_with_net_debt.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ebitda = grab(r"EBITDA is {N} USD million", text)
    mult = grab(r"EBITDA multiple is {N} times", text)
    debt = grab(r"total debt is {N} USD million", text)
    cash = grab(r"\bcash is {N} USD million", text)
    ev = ebitda * mult
    net_debt = debt - cash  # may be negative (net cash)
    return {"final": ev - net_debt, "slots": {"trace_1": ev, "trace_2": net_debt}}
