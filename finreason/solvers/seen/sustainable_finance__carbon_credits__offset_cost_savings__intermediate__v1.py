from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.offset_cost_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    emissions = grab(r"must offset {N} metric tons", text)
    price = grab(r"undiscounted price is {N} USD per credit", text)
    disc = grab(r"a {N} percent discount applies", text)

    gross = emissions * price
    discount = gross * disc / 100
    net = gross - discount
    return {
        "final": net,
        "slots": {
            "gross_cost_trace": gross,
            "discount_amount_trace": discount,
        },
    }
