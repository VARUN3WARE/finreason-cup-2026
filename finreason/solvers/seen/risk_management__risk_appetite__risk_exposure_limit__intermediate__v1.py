from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.risk_exposure_limit.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    assets = grab(r"Total assets are A\s*=\s*{N}", text)
    r_pct = grab(r"limit is r\s*=\s*{N}\s*percent", text)
    ratio = r_pct / 100
    exposure = assets * ratio
    return {"final": exposure, "slots": {"appetite_ratio_trace": ratio}}
