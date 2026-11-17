from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.scenario_planning.revenue_recovery_effect.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"Initial revenue is R\s*=\s*{N}", text)
    d = grab(r"downturn is d\s*=\s*{N}\s*percent", text)
    rec = grab(r"recovery applied to the reduced revenue is q\s*=\s*{N}\s*percent", text)
    remaining = 1 - d / 100
    multiple = 1 + rec / 100
    return {
        "final": rev * remaining * multiple,
        "slots": {
            "remaining_ratio_trace": remaining,
            "recovery_multiple_trace": multiple,
        },
    }
