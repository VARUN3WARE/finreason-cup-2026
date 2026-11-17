from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_dcf_valuation.advanced.v1"


def solve(text: str, q: dict) -> dict:
    fcf1 = grab(r"Year-1 free cash flow is {N}", text)
    g = grab(r"forecast growth is {N} percent", text) / 100
    r = grab(r"discount rate is {N} percent", text) / 100
    gt = grab(r"terminal growth is {N} percent", text) / 100
    pv_sum = Fraction(0)
    fcf = {}
    for t in range(1, 6):
        fcf[t] = fcf1 * (1 + g) ** (t - 1)
        pv_sum += fcf[t] / (1 + r) ** t
    tv = fcf[5] * (1 + gt) / (r - gt)
    ev = pv_sum + tv / (1 + r) ** 5
    return {"final": ev, "slots": {"trace_1": fcf[5], "trace_2": tv}}
