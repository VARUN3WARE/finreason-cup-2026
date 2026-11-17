from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_complex_net_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"cost bases are {N} and {N} USD million", text)
    rate = grab(r"saves {N} percent of their combined cost", text) / 100
    integ = grab(r"first-year integration cost is {N} USD million", text)
    combined = a + b
    gross = combined * rate
    net = gross - integ              # negative = first-year net cost, sign kept
    return {"final": net, "slots": {"trace_1": combined, "trace_2": gross}}
