from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_complex_after_tax.advanced.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"cost bases are {N} and {N} USD million", text)
    rate = grab(r"gross synergy rate is {N} percent", text) / 100
    integ = grab(r"one-time integration cost is {N} USD million", text)
    years = grab(r"amortization period is {N} years?", text)
    tax = grab(r"corporate tax rate is {N} percent", text) / 100
    gross = (a + b) * rate
    charge = integ / years
    pretax = gross - charge          # negative result kept (no floor)
    after_tax = pretax * (1 - tax)
    return {"final": after_tax, "slots": {"trace_1": gross, "trace_2": pretax}}
