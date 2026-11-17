"""h026 -- tweet/news/market signal aggregation with multi-stage moderation decay (literal transcription)."""

from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h026"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _stage_count(text: str) -> int:
    # "passes through exactly three sequential moderation stages"
    m = re.search(r"passes through (?:exactly )?(\w+) sequential moderation stages?", text)
    n_word = None
    if m:
        w = m.group(1).lower()
        n_word = int(w) if w.isdigit() else _WORDS.get(w)
    # "the final retention factor is (1-u)^3"
    m2 = re.search(r"final retention factor is \(1-u\)\^(\d+)", text)
    n_exp = int(m2.group(1)) if m2 else None
    if n_word is not None and n_exp is not None and n_word != n_exp:
        raise ValueError(f"stage count mismatch: {n_word} vs {n_exp}")
    n = n_word if n_word is not None else n_exp
    if n is None:
        raise ValueError("stage count not found")
    return n


def solve(text: str, q: dict) -> dict:
    # Sentence: "The raw tweet signal is {A} times signed average polarity {p}."
    tweet_mult = grab(r"raw tweet signal is {N} times", text)
    tweet_pol = grab(r"raw tweet signal is " + NUMBER + r" times signed average polarity {N}", text)
    raw_tweet = tweet_mult * tweet_pol

    # Sentence: "it passes through exactly N sequential moderation stages with no replenishment"
    n_stages = _stage_count(text)

    # Sentence: "At each stage, the same ratio u=... of the surviving signed signal is removed,
    #            so each stage retains 1-u and the final retention factor is (1-u)^N."
    u = grab(r"ratio u\s*=\s*{N}", text)
    per_stage_retention = 1 - u
    final_retention = per_stage_retention ** n_stages
    retained_tweet = raw_tweet * final_retention

    # Sentence: "The news contribution is {B} times signed average polarity {q} times influence factor {w}."
    news_mult = grab(r"news contribution is {N} times", text)
    news_pol = grab(r"news contribution is " + NUMBER + r" times signed average polarity {N}", text)
    news_infl = grab(r"news contribution is " + NUMBER + r" times signed average polarity "
                     + NUMBER + r" times influence factor {N}", text)
    news = news_mult * news_pol * news_infl

    # Sentence: "Add the retained tweet contribution, the news contribution, and the separate
    #            signed dimensionless market signal {M}."
    market = grab(r"signed dimensionless market signal {N}", text)
    aggregate = retained_tweet + news + market

    # Sentence: "Classify the exact aggregate as Bullish when it is at least {H},
    #            Bearish when it is at most the negative of {L}, and Neutral otherwise."
    bull_thr = grab(r"Bullish when it is at least {N}", text)
    m_neg = re.search(r"Bearish when it is at most the negative of (" + NUMBER + r")", text)
    if m_neg:
        bear_thr = -Fraction(m_neg.group(1).replace(",", ""))
    else:
        bear_thr = grab(r"Bearish when it is at most {N}", text)

    if aggregate >= bull_thr:
        final = "Bullish"
    elif aggregate <= bear_thr:
        final = "Bearish"
    else:
        final = "Neutral"

    return {
        "final": final,
        "slots": {"tweet_retention_factor_checkpoint": per_stage_retention},
    }
