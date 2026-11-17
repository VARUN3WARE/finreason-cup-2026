from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.bnpl_installment.basic.v1"


def solve(text: str, q: dict) -> dict:
    price = grab(r"purchase costs {N} USD", text)
    fee_pct = grab(r"service adds {N} percent", text)
    n = grab(r"across {N} installments", text)
    ratio = fee_pct / 100
    total = price * (1 + ratio)
    each = total / n if n != 0 else Fraction(0)
    return {"final": each, "slots": {"fee_ratio_trace": ratio, "total_due_trace": total}}
