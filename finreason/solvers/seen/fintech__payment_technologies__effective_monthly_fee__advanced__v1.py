from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.payment_technologies.effective_monthly_fee.advanced.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"processes {N} transactions", text)
    avg = grab(r"transactions averaging {N} USD", text)
    sub = grab(r"subscription {N} USD", text)
    flat = grab(r"flat fee {N} USD per transaction", text)
    r1 = grab(r"{N} percent on sales up to", text) / 100
    cap = grab(r"sales up to {N} USD", text)
    r2 = grab(r"{N} percent on sales above the cap", text) / 100
    sales = count * avg
    tier1 = min(sales, cap)
    tier2 = max(sales - cap, Fraction(0))
    total_fees = tier1 * r1 + tier2 * r2 + sub + flat * count
    rate = total_fees / sales * 100 if sales != 0 else Fraction(0)
    return {
        "final": rate,
        "slots": {
            "total_sales_trace": sales,
            "tier_two_sales_trace": tier2,
            "total_fees_trace": total_fees,
        },
    }
