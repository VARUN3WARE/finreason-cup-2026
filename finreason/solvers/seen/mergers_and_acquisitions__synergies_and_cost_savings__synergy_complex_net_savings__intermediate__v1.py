from fractions import Fraction

from finreason.nums import grab_all, grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_complex_net_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"cost bases are {N} and {N}", text)
    rate = grab(r"saves {N} percent", text) / 100
    integration = grab(r"integration cost is {N}", text)
    combined = a + b
    gross = combined * rate
    # Net = gross - integration; a negative result (net cost) keeps its sign.
    net = gross - integration
    return {"final": net, "slots": {"trace_1": combined, "trace_2": gross}}
