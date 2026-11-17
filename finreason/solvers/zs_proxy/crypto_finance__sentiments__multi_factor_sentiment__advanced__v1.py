from fractions import Fraction
from finreason.nums import grab_all

TEMPLATE_ID = "fp.crypto_finance.sentiments.multi_factor_sentiment.advanced.v1"


def solve(text: str, q: dict) -> dict:
    s_tweet, s_news, s_price = grab_all(
        r"tweet, news, and price signals of\s+{N},\s*{N},?\s+and\s+{N}", text)
    w_tweet, w_news, w_price = grab_all(
        r"weights are\s+{N},\s*{N},?\s+and\s+{N}", text)
    floor_, cap = grab_all(r"clips the weighted sum between\s+{N}\s+and\s+{N}", text)
    lo, hi = min(floor_, cap), max(floor_, cap)
    tweet_c = s_tweet * w_tweet
    news_c = s_news * w_news
    price_c = s_price * w_price
    raw = tweet_c + news_c + price_c
    clipped = min(max(raw, lo), hi)
    return {
        "final": clipped,
        "slots": {
            "tweet_component_trace": tweet_c,
            "news_component_trace": news_c,
            "raw_composite_trace": raw,
        },
    }
