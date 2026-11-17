from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.multi_company_synergy.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    e1 = grab(r"[Cc]ompany 1 must offset {N} metric tons", text)
    e2 = grab(r"[Cc]ompany 2 must offset {N} metric tons", text)
    price = grab(r"each credit costs {N} USD", text)
    disc = grab(r"{N} percent discount", text) / 100
    threshold = grab(r"combined credit quantity is strictly greater than {N}", text)
    total = e1 + e2  # one credit per metric ton
    gross = total * price
    discounted = gross * (1 - disc)
    final = discounted if total > threshold else gross  # strict; equality does not qualify
    return {
        "final": final,
        "slots": {
            "total_credits_trace": total,
            "gross_cost_trace": gross,
            "discounted_cost_trace": discounted,
        },
    }
