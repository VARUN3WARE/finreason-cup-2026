from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.scenario_planning.market_downturn_revenue.basic.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"Initial revenue is R\s*=\s*{N}", text)
    d = grab(r"downturn is d\s*=\s*{N}\s*percent", text)
    remaining = 1 - d / 100
    return {"final": rev * remaining, "slots": {"remaining_ratio_trace": remaining}}
