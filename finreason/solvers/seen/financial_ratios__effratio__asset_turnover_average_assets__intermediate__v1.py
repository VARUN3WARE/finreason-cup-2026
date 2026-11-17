from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.effratio.asset_turnover_average_assets.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Nn]et sales (?:are|of|were) {N}", text)
    begin = grab(r"beginning total assets (?:are|of|were) {N}", text)
    end = grab(r"ending total assets (?:are|of|were) {N}", text)
    avg = (begin + end) / 2
    return {"final": sales / avg, "slots": {"trace_1": avg}}
