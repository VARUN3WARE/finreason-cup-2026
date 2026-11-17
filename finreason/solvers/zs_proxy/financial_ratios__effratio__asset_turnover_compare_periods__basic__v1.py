import re
from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.effratio.asset_turnover_compare_periods.basic.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"[Nn]et sales (?:are|of|were) {N}", text)
    prior_assets = grab(r"[Aa]verage total assets were {N}", text)
    delta = grab(r"(?:increase|decrease)s? by {N}", text)
    m = re.search(r"(increase|decrease)s? by", text)
    if m.group(1) == "decrease":
        delta = -delta
    cur_assets = prior_assets + delta
    prior_t = sales / prior_assets
    cur_t = sales / cur_assets
    return {"final": prior_t - cur_t, "slots": {"trace_1": prior_t, "trace_2": cur_t}}
