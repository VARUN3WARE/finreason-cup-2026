from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.batch_effective_fee.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    sales = grab(r"total sales of {N} USD", text)
    count = grab(r"across {N} transactions", text)
    fixed_fee = grab(r"Pricing is {N} USD per transaction", text)
    var_pct = grab(r"plus {N} percent of total sales", text)
    var_ratio = var_pct / 100
    fixed_total = count * fixed_fee
    variable_total = sales * var_ratio
    total_fees = fixed_total + variable_total
    eff_pct = total_fees / sales * 100
    return {
        "final": eff_pct,
        "slots": {
            "fixed_fee_total_trace": fixed_total,
            "variable_fee_total_trace": variable_total,
            "total_fees_trace": total_fees,
        },
    }
