from fractions import Fraction
import re
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.tokenomics.staking_reward_effect.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    supply = grab(r"has {N} units", text)
    price = grab(r"initial price of {N} USD per token", text)
    lock = grab(r"locks {N} percent", text) / 100
    m = re.search(r"scenario (increases|decreases|raises|lowers|reduces|changes) price by", text)
    chg = grab(r"price by {N} percent", text) / 100
    if m and m.group(1) in ("decreases", "lowers", "reduces"):
        chg = -chg
    eff_supply = supply * (1 - lock)
    adj_price = price * (1 + chg)
    return {
        "final": eff_supply * adj_price,
        "slots": {"effective_supply_trace": eff_supply, "adjusted_price_trace": adj_price},
    }
