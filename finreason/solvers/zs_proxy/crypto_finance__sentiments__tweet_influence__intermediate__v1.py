from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.tweet_influence.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    n = grab(r"contains\s+{N}\s+influential tweets", text)
    pol = grab(r"average polarity is\s+{N}", text)
    eng = grab(r"engagement weight is\s+{N}\s*percent", text) / 100
    total = n * pol
    return {
        "final": total * eng,
        "slots": {
            "engagement_ratio_trace": eng,
            "polarity_total_trace": total,
        },
    }
