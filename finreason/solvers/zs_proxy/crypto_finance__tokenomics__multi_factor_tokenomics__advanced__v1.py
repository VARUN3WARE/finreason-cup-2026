from fractions import Fraction
import re
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.tokenomics.multi_factor_tokenomics.advanced.v1"


def solve(text: str, q: dict) -> dict:
    supply = grab(r"begins with {N} units", text)
    price = grab(r"at {N} USD per token", text)
    burn = grab(r"burns {N} percent", text) / 100
    emit = grab(r"emits {N} percent", text) / 100
    try:
        react = grab(r"market reaction (?:changes|moves|shifts) price by {N} percent", text) / 100
    except ValueError:
        react = grab(r"price by {N} percent", text) / 100
    m = re.search(r"market reaction (increases|decreases|raises|lowers|reduces)", text)
    if m and m.group(1) in ("decreases", "lowers", "reduces"):
        react = -abs(react)
    post_burn = supply * (1 - burn)
    adj_supply = post_burn * (1 + emit)
    adj_price = price * (1 + react)
    return {
        "final": adj_supply * adj_price,
        "slots": {
            "post_burn_supply_trace": post_burn,
            "adjusted_supply_trace": adj_supply,
            "adjusted_price_trace": adj_price,
        },
    }
