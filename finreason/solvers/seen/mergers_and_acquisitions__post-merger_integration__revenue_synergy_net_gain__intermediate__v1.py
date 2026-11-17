from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.revenue_synergy_net_gain.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"[Oo]verlapping annual revenue at Company A is {N} USD million", text)
    b = grab(r"[Oo]verlapping annual revenue at Company B is {N} USD million", text)
    uplift = grab(r"cross-selling uplift is {N} percent", text) / 100
    cannib = grab(r"cannibalization loss is {N} percent", text) / 100
    combined = a + b
    gross = combined * uplift
    loss = combined * cannib
    return {"final": gross - loss, "slots": {"trace_1": combined, "trace_2": gross}}
