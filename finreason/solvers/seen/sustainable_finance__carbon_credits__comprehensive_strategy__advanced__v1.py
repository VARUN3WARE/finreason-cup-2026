from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.comprehensive_strategy.advanced.v1"


def solve(text: str, q: dict) -> dict:
    invest = grab(r"spends exactly {N} USD", text)
    base = grab(r"base price is {N} USD per credit", text)
    disc = grab(r"{N} percent purchase discount", text)
    target = grab(r"retains up to {N} purchased credits", text)
    prem = grab(r"sold at a {N} percent premium", text)
    rebate = grab(r"fixed rebate of {N} USD", text)

    price = base * (1 - disc / 100)
    credits = invest / price
    surplus = max(Fraction(0), credits - target)
    sale_price = price * (1 + prem / 100)
    revenue = surplus * sale_price
    net = revenue + rebate - invest
    return {
        "final": net,
        "slots": {
            "discounted_price_trace": price,
            "credits_purchased_trace": credits,
            "surplus_credits_trace": surplus,
        },
    }
