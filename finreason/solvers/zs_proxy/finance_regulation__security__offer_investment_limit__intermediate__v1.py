from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.offer_investment_limit.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    income = grab(r"Annual income in USD is {N}", text)
    worth = grab(r"Net worth in USD is {N}", text)
    prop = grab(r"Proposed investment in USD is {N}", text)
    pct = grab(r"limit is exactly {N} percent", text)
    base = max(income, worth)
    limit = base * pct / 100
    allowed = prop <= limit  # at most, including equality
    return {
        "final": "true" if allowed else "false",
        "slots": {"financial_base_usd": base, "investment_limit_usd": limit},
    }
