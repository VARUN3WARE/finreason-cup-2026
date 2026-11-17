import re

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.kyc.source_of_funds.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    source = grab(r"source risk score is {N}", text)
    juris = grab(r"jurisdiction risk score is {N}", text)
    amount = grab(r"deposit amount in whole USD is {N}", text)
    trace = re.search(r"evidence traceability is (\w+)\.", text).group(1)

    total = source + juris

    rm = re.search(
        rf"route applies exactly when the amount is (at least|above) USD ({NUMBER}) and traceability is (\w+)",
        text,
    )
    if rm is None:
        raise ValueError("route rule not found")
    thr = F(rm.group(2))
    amt_ok = amount >= thr if rm.group(1) == "at least" else amount > thr
    route_hit = amt_ok and trace == rm.group(3)
    route = "high_value_low_traceability_route" if route_hit else "standard_amount_route"

    high_min = grab(r"high_risk when the total score is at least {N}", text)
    med_min = grab(r"medium_risk when the total is at least {N}", text)
    if total >= high_min or route_hit:
        final = "high_risk"
    elif total >= med_min:
        final = "medium_risk"
    else:
        final = "low_risk"

    return {
        "final": final,
        "slots": {"total_risk_score": total, "amount_traceability_route": route},
    }
