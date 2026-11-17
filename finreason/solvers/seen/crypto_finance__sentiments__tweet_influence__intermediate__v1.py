from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.tweet_influence.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"contains {N} influential tweets", text)
    polarity = grab(r"signed average polarity is {N}", text)
    engagement = grab(r"engagement weight is {N} percent", text) / 100
    polarity_total = count * polarity
    return {
        "final": polarity_total * engagement,
        "slots": {
            "engagement_ratio_trace": engagement,
            "polarity_total_trace": polarity_total,
        },
    }
