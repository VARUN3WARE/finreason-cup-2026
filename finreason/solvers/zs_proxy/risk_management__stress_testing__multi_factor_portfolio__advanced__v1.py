from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.stress_testing.multi_factor_portfolio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    v = grab(r"\bV\s*=\s*{N}", text)
    qc = grab(r"\bqc\s*=\s*{N}", text)
    qm = grab(r"\bqm\s*=\s*{N}", text)
    sc = grab(r"\bsc\s*=\s*{N}", text)
    sm = grab(r"\bsm\s*=\s*{N}", text)
    credit = v * (qc / 100) * sc
    market = v * (qm / 100) * sm
    return {"final": credit + market,
            "slots": {"credit_impact_trace": credit, "market_impact_trace": market}}
