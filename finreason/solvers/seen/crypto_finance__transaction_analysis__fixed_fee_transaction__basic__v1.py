from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.fixed_fee_transaction.basic.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross value {N} USD", text)
    fee = grab(r"fixed processing fee of {N} USD", text)
    return {"final": gross - fee, "slots": {}}
