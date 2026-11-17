from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.effective_monthly_fee.advanced.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"processes {N} transactions", text)
    avg = grab(r"averaging {N} USD", text)
    subscription = grab(r"subscription {N} USD", text)
    flat = grab(r"flat fee {N} USD per transaction", text)
    r1_pct = grab(r"{N} percent on sales up to", text)
    cap = grab(r"on sales up to {N} USD", text)
    r2_pct = grab(r"{N} percent on sales above", text)

    total_sales = count * avg
    tier_one = min(total_sales, cap)
    tier_two = max(total_sales - cap, Fraction(0))
    r1 = r1_pct / 100
    r2 = r2_pct / 100
    tier_fees = tier_one * r1 + tier_two * r2
    total_fees = tier_fees + subscription + flat * count
    eff_pct = total_fees / total_sales * 100
    return {
        "final": eff_pct,
        "slots": {
            "total_sales_trace": total_sales,
            "tier_two_sales_trace": tier_two,
            "total_fees_trace": total_fees,
        },
    }
