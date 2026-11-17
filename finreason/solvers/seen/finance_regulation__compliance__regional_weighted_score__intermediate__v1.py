"""Regional weighted compliance score: sum of score*weight per region, no normalization."""

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.regional_weighted_score.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    sa = grab(r"Region A risk score is {N}", text)
    sb = grab(r"Region B risk score is {N}", text)
    wa = grab(r"Region A supplied weight is {N}", text)
    wb = grab(r"Region B supplied weight is {N}", text)
    ca = sa * wa
    cb = sb * wb
    return {"final": ca + cb, "slots": {"region_a_component": ca, "region_b_component": cb}}
