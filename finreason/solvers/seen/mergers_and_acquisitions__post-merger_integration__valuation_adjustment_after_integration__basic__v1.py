from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.valuation_adjustment_after_integration.basic.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"[Pp]re-merger valuation of Company A is {N} USD million", text)
    b = grab(r"[Pp]re-merger valuation of Company B is {N} USD million", text)
    prem = grab(r"integration premium is {N} percent", text) / 100
    combined = a + b
    factor = 1 + prem
    return {"final": combined * factor, "slots": {"trace_1": combined, "trace_2": factor}}
