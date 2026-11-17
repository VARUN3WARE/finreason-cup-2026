from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.revenue_synergy_net_gain.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"annual revenue at Company A is {N}", text)
    b = grab(r"annual revenue at Company B is {N}", text)
    up = grab(r"cross-selling uplift is {N} percent", text) / 100
    cann = grab(r"cannibalization loss is {N} percent", text) / 100
    combined = a + b
    gross = combined * up
    loss = combined * cann
    net = gross - loss
    return {"final": net, "slots": {"trace_1": combined, "trace_2": gross}}
