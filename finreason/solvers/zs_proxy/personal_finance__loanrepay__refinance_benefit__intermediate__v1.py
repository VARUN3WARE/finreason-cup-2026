from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.loanrepay.refinance_benefit.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    old_int = grab(r"old-loan interest in USD is {N}", text)
    new_int = grab(r"new-loan interest in USD is {N}", text)
    fee = grab(r"Refinancing fee in USD is {N}", text)
    gross = old_int - new_int
    net = gross - fee  # may be negative; no floor
    return {"final": net, "slots": {"gross_interest_savings_usd": gross}}
