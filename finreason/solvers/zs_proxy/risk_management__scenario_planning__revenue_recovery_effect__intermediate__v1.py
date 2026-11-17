from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.scenario_planning.revenue_recovery_effect.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rev = grab(r"[Ii]nitial revenue is\s+R\s*=\s*{N}", text)
    d = grab(r"downturn is\s+d\s*=\s*{N}\s*percent", text)
    rq = grab(r"recovery applied to the reduced revenue is\s+q\s*=\s*{N}\s*percent", text)
    remaining = 1 - d / 100
    recovery = 1 + rq / 100
    return {
        "final": rev * remaining * recovery,
        "slots": {"remaining_ratio_trace": remaining, "recovery_multiple_trace": recovery},
    }
