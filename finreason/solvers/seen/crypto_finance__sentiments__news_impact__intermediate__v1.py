from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.sentiments.news_impact.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"contains {N} articles", text)
    sentiment = grab(r"signed average sentiment is {N}", text)
    quality = grab(r"source-quality weight is {N}", text)
    influence = grab(r"influence weight is {N} percent", text) / 100
    quality_sentiment = sentiment * quality
    final = count * quality_sentiment * influence
    return {
        "final": final,
        "slots": {
            "quality_sentiment_trace": quality_sentiment,
            "influence_ratio_trace": influence,
        },
    }
