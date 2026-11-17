from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.tokenomics.emission_schedule_impact.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    supply = grab(r"has {N} (?:token )?units", text)
    price = grab(r"price of {N} USD per token", text)
    ratio = grab(r"emits new tokens equal to {N} percent", text) / 100
    new_supply = supply * (1 + ratio)
    return {
        "final": new_supply * price,
        "slots": {"emission_ratio_trace": ratio, "new_supply_trace": new_supply},
    }
