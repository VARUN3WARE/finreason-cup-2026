from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.integration_cost_reduction.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"[Oo]verlapping operating costs are {N} and {N} USD million", text)
    rate = grab(r"overlap reduction rate is {N} percent", text) / 100
    integ = grab(r"one-time integration cost is {N} USD million", text)
    combined = a + b
    gross = combined * rate
    net = gross - integ
    return {"final": net, "slots": {"trace_1": combined, "trace_2": gross}}
