from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_metrics.multi_factor_portfolio.advanced.v1"

_SLOTS = ("impact_one_trace", "impact_two_trace", "impact_three_trace")


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}\s*USD", text)
    impacts = []
    for i in (1, 2, 3):
        w = grab(rf"\bw{i}\s*=\s*{{N}}", text)
        c = grab(rf"\bc{i}\s*=\s*{{N}}", text)
        s = grab(rf"\bs{i}\s*=\s*{{N}}", text)
        impacts.append(v * (w / 100) * (c / 100) * s)
    total = sum(impacts, Fraction(0))
    return {"final": total, "slots": dict(zip(_SLOTS, impacts))}
