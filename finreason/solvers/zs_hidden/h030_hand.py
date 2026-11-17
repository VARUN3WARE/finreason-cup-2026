from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h030"


def solve(text: str, q: dict) -> dict:
    base = grab(r"base assessment {N}\s*USD", text)
    days = grab(r"reporting delay of {N} days", text)
    per_day = grab(r"incurs {N}\s*USD per day", text)
    credit = grab(r"Treat {N} as the fractional credit", text)
    monitoring = grab(r"monitoring cost {N}\s*USD", text)

    combined = base + days * per_day          # credit base: assessment + delay charge
    retained = 1 - credit                     # retained fraction
    total = combined * retained + monitoring  # monitoring added outside the credit base
    return {"final": total, "slots": {"post_credit_factor_checkpoint": retained}}
