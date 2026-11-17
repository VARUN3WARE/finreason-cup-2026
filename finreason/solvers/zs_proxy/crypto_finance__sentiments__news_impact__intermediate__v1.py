from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.news_impact.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    n = grab(r"contains\s+{N}\s+articles", text)
    sent = grab(r"average sentiment is\s+{N}", text)
    quality = grab(r"source-quality weight is\s+{N}", text)
    infl = grab(r"influence weight is\s+{N}\s*percent", text) / 100
    quality_sent = sent * quality
    final = n * quality_sent * infl
    return {
        "final": final,
        "slots": {
            "quality_sentiment_trace": quality_sent,
            "influence_ratio_trace": infl,
        },
    }
