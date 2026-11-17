from fractions import Fraction

from finreason.nums import grab_all, grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_complex_after_tax.advanced.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"cost bases are {N} and {N}", text)
    rate = grab(r"gross synergy rate is {N} percent", text) / 100
    integration = grab(r"one-time integration cost is {N}", text)
    years = grab(r"amortization period is {N} years?", text)
    tax = grab(r"corporate tax rate is {N} percent", text) / 100
    gross = (a + b) * rate
    annual_charge = integration / years
    pre_tax = gross - annual_charge
    # "A negative result remains negative": no floor, tax applied symmetrically.
    after_tax = pre_tax * (1 - tax)
    return {"final": after_tax, "slots": {"trace_1": gross, "trace_2": pre_tax}}
