from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.transaction_fee_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross value {N} USD", text)
    fee = grab(r"a fee of {N} percent", text) / 100
    retained = 1 - fee
    return {"final": gross * retained, "slots": {"retained_ratio_trace": retained}}
