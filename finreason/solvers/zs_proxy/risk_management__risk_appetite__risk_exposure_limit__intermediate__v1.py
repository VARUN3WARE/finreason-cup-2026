from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.risk_appetite.risk_exposure_limit.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"\bA\s*=\s*{N}", text)             # total assets, USD
    r = grab(r"\br\s*=\s*{N}\s*percent", text)   # risk-appetite limit, percent
    ratio = r / 100
    exposure = a * ratio
    return {"final": exposure, "slots": {"appetite_ratio_trace": ratio}}
