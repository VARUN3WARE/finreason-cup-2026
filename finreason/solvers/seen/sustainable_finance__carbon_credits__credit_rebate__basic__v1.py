from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.credit_rebate.basic.v1"


def solve(text: str, q: dict) -> dict:
    invest = grab(r"buyer invests {N} USD", text)
    price = grab(r"priced at {N} USD per credit", text)
    rate = grab(r"rebate is {N} USD per purchased credit", text)
    threshold = grab(r"strictly greater than {N} credits", text)

    qty = invest / price
    # Preselection rebate amount (reported regardless of eligibility).
    eligible = qty * rate
    final = eligible if qty > threshold else Fraction(0)
    return {
        "final": final,
        "slots": {
            "credits_purchased_trace": qty,
            "eligible_rebate_trace": eligible,
        },
    }
