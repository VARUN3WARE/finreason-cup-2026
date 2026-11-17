from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.batch_effective_fee.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"total sales of {N} USD", text)
    count = grab(r"across {N} transactions", text)
    fixed = grab(r"Pricing is {N} USD per transaction", text)
    var_pct = grab(r"plus {N} percent of total sales", text)
    fixed_total = count * fixed
    var_total = sales * (var_pct / 100)
    total_fees = fixed_total + var_total
    # Effective rate = total fees / total sales, in percent (undefined at zero sales -> 0).
    rate = total_fees / sales * 100 if sales != 0 else Fraction(0)
    return {
        "final": rate,
        "slots": {
            "fixed_fee_total_trace": fixed_total,
            "variable_fee_total_trace": var_total,
            "total_fees_trace": total_fees,
        },
    }
