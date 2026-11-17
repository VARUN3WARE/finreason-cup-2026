from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.crypto_finance.whale_detection.multiple_transaction_analysis.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    t1, t2, t3 = grab_all(r"transfers of (?:USD )?{N},\s*{N},?\s*and\s*{N}", text)
    threshold = grab(r"threshold of (?:USD )?{N}", text)
    ex = [max(t - threshold, Fraction(0)) for t in (t1, t2, t3)]
    return {
        "final": ex[0] + ex[1] + ex[2],
        "slots": {
            "excess_one_trace": ex[0],
            "excess_two_trace": ex[1],
            "excess_three_trace": ex[2],
        },
    }
