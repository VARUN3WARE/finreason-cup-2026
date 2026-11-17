from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.basel.tier1_composition.basic.v1"


def solve(text: str, q: dict) -> dict:
    ce = grab(r"[Cc]ommon equity in USD millions is {N}", text)
    at1 = grab(r"Additional Tier 1 amount in USD millions is {N}", text)
    total = grab(r"Total Tier 1 capital in USD millions is {N}", text)
    eligible = ce + at1
    ratio = eligible / total
    return {
        "final": ratio * 100,  # exact; framework rounds half up to 2 dp
        "slots": {"eligible_tier1_usd_million": eligible, "composition_ratio": ratio},
    }
