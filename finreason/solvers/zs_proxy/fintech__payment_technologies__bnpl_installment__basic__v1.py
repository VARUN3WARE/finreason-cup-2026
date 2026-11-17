from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.bnpl_installment.basic.v1"


def solve(text: str, q: dict) -> dict:
    price = grab(r"purchase costs {N} USD", text)
    fee_pct = grab(r"service adds {N} percent", text)
    n = grab(r"across {N} installments", text)
    fee_ratio = fee_pct / 100
    total_due = price * (1 + fee_ratio)
    installment = total_due / n
    return {
        "final": installment,
        "slots": {
            "fee_ratio_trace": fee_ratio,
            "total_due_trace": total_due,
        },
    }
