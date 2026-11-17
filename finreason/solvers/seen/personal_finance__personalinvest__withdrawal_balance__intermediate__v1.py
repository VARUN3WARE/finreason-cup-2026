from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.personalinvest.withdrawal_balance.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    start = grab(r"Starting balance in USD is {N}", text)
    withdrawal = grab(r"Withdrawal in USD is {N}", text)
    fee_ratio = grab(r"Fee ratio is {N}", text)
    fee = withdrawal * fee_ratio
    outflow = withdrawal + fee
    ending = start - outflow  # may be negative per the text; no floor
    return {"final": ending, "slots": {"withdrawal_fee_usd": fee, "total_outflow_usd": outflow}}
