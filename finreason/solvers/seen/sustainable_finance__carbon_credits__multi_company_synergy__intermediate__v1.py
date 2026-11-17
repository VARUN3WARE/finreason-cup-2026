from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.multi_company_synergy.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    t1 = grab(r"Company 1 must offset {N} metric tons", text)
    t2 = grab(r"company 2 must offset {N} metric tons", text)
    price = grab(r"each credit costs {N} USD", text)
    disc = grab(r"A {N} percent discount", text)
    threshold = grab(r"combined credit quantity is strictly greater than {N}", text)

    total = t1 + t2
    gross = total * price
    discounted = gross * (1 - disc / 100)
    final = discounted if total > threshold else gross
    return {
        "final": final,
        "slots": {
            "total_credits_trace": total,
            "gross_cost_trace": gross,
            "discounted_cost_trace": discounted,
        },
    }
