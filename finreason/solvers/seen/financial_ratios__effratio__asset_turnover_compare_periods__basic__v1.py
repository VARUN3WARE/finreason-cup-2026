import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "fp.financial_ratios.effratio.asset_turnover_compare_periods.basic.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Nn]et sales (?:are|of|were) {N}", text)
    prior_assets = grab(r"[Aa]verage total assets (?:were|are|of) {N}", text)
    m = re.search(rf"(increase|decrease|rise|fall|decline)s? by ({NUMBER})", text)
    if m is None:
        raise ValueError("asset change not found")
    delta = Fraction(m.group(2).replace(",", ""))
    if m.group(1) in ("decrease", "fall", "decline"):
        delta = -delta
    cur_assets = prior_assets + delta
    prior_t = sales / prior_assets
    cur_t = sales / cur_assets
    # "decline in asset turnover: prior-period turnover minus current-period turnover"
    return {"final": prior_t - cur_t, "slots": {"trace_1": prior_t, "trace_2": cur_t}}
