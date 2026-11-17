from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.offer_investment_limit.intermediate.v1"


def _bool(flag: bool) -> str:
    return "true" if flag else "false"


def solve(text: str, q: dict) -> dict:
    income = grab(r"Annual income in USD is {N}", text)
    net_worth = grab(r"Net worth in USD is {N}", text)
    proposal = grab(r"Proposed investment in USD is {N}", text)
    pct = grab(r"limit is (?:exactly )?{N} percent of the larger", text)
    # Base = larger of income and net worth (ties: same value either way).
    base = max(income, net_worth)
    limit = base * pct / 100
    # Allowed when at most the limit, including equality.
    allowed = proposal <= limit
    return {
        "final": _bool(allowed),
        "slots": {"financial_base_usd": base, "investment_limit_usd": limit},
    }
