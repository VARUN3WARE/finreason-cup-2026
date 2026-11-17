from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.personalinvest.withdrawal_balance.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    start = grab(r"Starting balance in USD is {N}", text)
    wd = grab(r"Withdrawal in USD is {N}", text)
    ratio = grab(r"Fee ratio is {N}", text)
    fee = wd * ratio
    outflow = wd + fee
    ending = start - outflow  # may be negative; no floor
    return {"final": ending, "slots": {"withdrawal_fee_usd": fee, "total_outflow_usd": outflow}}
