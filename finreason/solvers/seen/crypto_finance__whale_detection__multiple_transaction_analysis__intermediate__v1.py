from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.crypto_finance.whale_detection.multiple_transaction_analysis.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    t1, t2, t3 = grab_all(r"transfers of {N},\s*{N},?\s*and\s*{N}\s*USD", text)
    threshold = grab(r"threshold of {N}\s*USD", text)

    def excess(t: Fraction) -> Fraction:
        d = t - threshold
        return d if d > 0 else Fraction(0)

    e1, e2, e3 = excess(t1), excess(t2), excess(t3)
    return {
        "final": e1 + e2 + e3,
        "slots": {
            "excess_one_trace": e1,
            "excess_two_trace": e2,
            "excess_three_trace": e3,
        },
    }
