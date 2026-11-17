from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.effratio.asset_turnover_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"net sales (?:of|are|were) {N}", text)
    assets = grab(r"average total assets (?:of|are|were) {N}", text)
    return {"final": sales / assets, "slots": {}}
