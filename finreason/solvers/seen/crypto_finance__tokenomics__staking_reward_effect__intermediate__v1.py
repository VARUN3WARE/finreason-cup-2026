import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.tokenomics.staking_reward_effect.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    supply = grab(r"has {N} (?:token )?units", text)
    price = grab(r"initial price of {N} USD per token", text)
    lock = grab(r"locks {N} percent of supply", text) / 100
    m = re.search(r"(increases|decreases|changes) price by", text)
    change = grab(r"(?:increases|decreases|changes) price by {N} percent", text) / 100
    if m is not None and m.group(1) == "decreases":
        change = -change
    eff_supply = supply * (1 - lock)
    adj_price = price * (1 + change)
    return {
        "final": eff_supply * adj_price,
        "slots": {"effective_supply_trace": eff_supply, "adjusted_price_trace": adj_price},
    }
