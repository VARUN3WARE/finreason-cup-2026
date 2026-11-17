from fractions import Fraction

from finreason.nums import grab_all

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.bulk_transaction_fees.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a1, a2, a3 = grab_all(r"three transfers of {N},? {N},? and {N} USD", text)
    f1, f2, f3 = grab_all(r"fee rates are {N},? {N},? and {N} percent", text)
    n1 = a1 * (1 - f1 / 100)
    n2 = a2 * (1 - f2 / 100)
    n3 = a3 * (1 - f3 / 100)
    return {
        "final": n1 + n2 + n3,
        "slots": {"net_one_trace": n1, "net_two_trace": n2, "net_three_trace": n3},
    }
