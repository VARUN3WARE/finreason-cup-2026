from fractions import Fraction

from finreason.nums import grab_all

TEMPLATE_ID = "fp.crypto_finance.sentiments.multi_factor_sentiment.advanced.v1"


def solve(text: str, q: dict) -> dict:
    s_tweet, s_news, s_price = grab_all(r"tweet, news, and price signals of {N},\s*{N},\s*and\s*{N}", text)
    w_tweet, w_news, w_price = grab_all(r"weights are {N},\s*{N},\s*and\s*{N}", text)
    floor, cap = grab_all(r"clips the weighted sum between {N} and {N}", text)
    tweet_c = s_tweet * w_tweet
    news_c = s_news * w_news
    price_c = s_price * w_price
    raw = tweet_c + news_c + price_c
    # Stated order: larger of sum and floor, then smaller of that and cap.
    clipped = min(max(raw, floor), cap)
    return {
        "final": Fraction(clipped),
        "slots": {
            "tweet_component_trace": tweet_c,
            "news_component_trace": news_c,
            "raw_composite_trace": raw,
        },
    }
