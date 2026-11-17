from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.energy_efficiency_savings.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"annual energy cost of (?:USD )?{N}", text)
    ratio = grab(r"reduces that cost by {N} percent", text) / 100
    return {"final": cost * (1 - ratio), "slots": {"saving_ratio_trace": ratio}}
