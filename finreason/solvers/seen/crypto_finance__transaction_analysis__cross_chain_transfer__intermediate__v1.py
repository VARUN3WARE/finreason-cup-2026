from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.cross_chain_transfer.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    initial = grab(r"transfer begins at {N} USD", text)
    fee = grab(r"bridge charges {N} percent", text) / 100
    bonus = grab(r"fixed local bonus of {N} USD", text)
    retained = 1 - fee
    after_fee = initial * retained
    return {
        "final": after_fee + bonus,
        "slots": {"retained_ratio_trace": retained, "after_fee_trace": after_fee},
    }
