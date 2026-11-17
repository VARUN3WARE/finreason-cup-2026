from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.scenario_planning.investment_scenario_planning.advanced.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"[Ii]nitial investment is\s+V\s*=\s*{N}", text)
    cm = grab(r"\bcm\s*=\s*{N}", text)
    ci = grab(r"\bci\s*=\s*{N}", text)
    cf = grab(r"\bcf\s*=\s*{N}", text)
    sm = grab(r"\bsm\s*=\s*{N}", text)
    si = grab(r"\bsi\s*=\s*{N}", text)
    sf = grab(r"\bsf\s*=\s*{N}", text)
    market = sm * cm / 100
    interest = si * ci / 100
    inflation = sf * cf / 100
    delta = v * (market + interest + inflation)
    return {
        "final": delta,
        "slots": {
            "market_effect_trace": market,
            "interest_effect_trace": interest,
            "inflation_effect_trace": inflation,
        },
    }
