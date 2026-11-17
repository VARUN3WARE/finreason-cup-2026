from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.loanrepay.extra_payment_total.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    scheduled = grab(r"Scheduled monthly payment in USD is {N}", text)
    extra = grab(r"Extra monthly payment in USD is {N}", text)
    months = grab(r"month count is {N}", text)
    combined = scheduled + extra
    total = combined * months  # final rounding done by framework (half up, 2dp)
    return {"final": total, "slots": {"combined_monthly_payment": combined}}
