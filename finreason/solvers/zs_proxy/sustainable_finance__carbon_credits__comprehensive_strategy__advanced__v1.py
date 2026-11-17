from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.carbon_credits.comprehensive_strategy.advanced.v1"


def solve(text: str, q: dict) -> dict:
    invest = grab(r"spends exactly {N} USD", text)
    base = grab(r"base price is {N} USD per credit", text)
    disc = grab(r"{N} percent purchase discount", text) / 100
    target = grab(r"retains up to {N} purchased credits", text)
    premium = grab(r"sold at an? {N} percent premium", text) / 100
    rebate = grab(r"fixed rebate of {N} USD", text)
    dprice = base * (1 - disc)
    credits = invest / dprice
    surplus = max(Fraction(0), credits - target)
    revenue = surplus * dprice * (1 + premium)
    final = revenue + rebate - invest
    return {
        "final": final,
        "slots": {
            "discounted_price_trace": dprice,
            "credits_purchased_trace": credits,
            "surplus_credits_trace": surplus,
        },
    }
