from fractions import Fraction
from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.bulk_transaction_fees.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    amts = grab_all(r"transfers of\s+{N},\s*{N},?\s*and\s+{N}\s*USD", text)
    rates = grab_all(r"fee rates are\s+{N},\s*{N},?\s*and\s+{N}\s*percent", text)
    assert len(amts) == 3 and len(rates) == 3
    nets = [a * (1 - r / 100) for a, r in zip(amts, rates)]
    return {
        "final": sum(nets, Fraction(0)),
        "slots": {
            "net_one_trace": nets[0],
            "net_two_trace": nets[1],
            "net_three_trace": nets[2],
        },
    }
