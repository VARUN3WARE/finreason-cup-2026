from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.cross_chain_transfer.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    v0 = grab(r"transfer begins at\s+{N}\s*USD", text)
    fee = grab(r"bridge charges\s+{N}\s*percent", text) / 100
    bonus = grab(r"fixed local bonus of\s+{N}\s*USD", text)
    retained = 1 - fee
    after_fee = v0 * retained
    return {
        "final": after_fee + bonus,
        "slots": {"retained_ratio_trace": retained, "after_fee_trace": after_fee},
    }
