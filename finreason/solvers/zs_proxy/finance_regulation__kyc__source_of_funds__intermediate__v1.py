"""Source-of-funds rating: total = source + jurisdiction score; high-value/low-traceability route."""
import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.kyc.source_of_funds.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    src = grab(r"source risk score is {N}", text)
    jur = grab(r"jurisdiction risk score is {N}", text)
    amount = grab(r"deposit amount in whole USD is {N}", text)
    trace = re.search(r"evidence traceability is ([a-z_]+)", text).group(1)

    try:
        amt_min = grab(r"amount is at least USD {N} and traceability is low", text)
    except ValueError:
        amt_min = Fraction(100000)
    try:
        high_min = grab(r"high_risk when the total score is at least {N}", text)
    except ValueError:
        high_min = Fraction(12)
    try:
        med_min = grab(r"medium_risk when the total is at least {N}", text)
    except ValueError:
        med_min = Fraction(8)

    total = src + jur
    route_hit = amount >= amt_min and trace == "low"
    route = "high_value_low_traceability_route" if route_hit else "standard_amount_route"

    if total >= high_min or route_hit:
        final = "high_risk"
    elif total >= med_min:
        final = "medium_risk"
    else:
        final = "low_risk"
    return {"final": final, "slots": {"total_risk_score": total, "amount_traceability_route": route}}
