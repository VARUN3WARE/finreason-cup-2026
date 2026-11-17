"""h093 -- sentiment model: solve for the tweet engagement ratio that reaches a target total score.

Literal transcription:
  "must reach a total score of T"
  "news contribution equals A multiplied by average news polarity Pn and influence factor I"
      -> news = A * Pn * I
  "tweet contribution equals B multiplied by average tweet polarity Pt and an unknown engagement ratio"
      -> tweet = B * Pt * E
  "The total score is the sum of these two contributions" -> T = news + tweet
  "What engagement ratio reaches the target?" -> E = (T - news) / (B * Pt)
Checkpoint: weighted news contribution = news.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h093"


def solve(text: str, q: dict) -> dict:
    # Sentence 1: target total score.
    total_target = grab(r"total score of {N}", text)

    # Sentence 2: news contribution = A * average news polarity * influence factor.
    news_mult = grab(r"news contribution equals {N} multiplied by", text)
    news_polarity = grab(r"average news polarity {N}", text)
    influence_factor = grab(r"influence factor {N}", text)
    news_contribution = news_mult * news_polarity * influence_factor

    # Sentence 3: tweet contribution = B * average tweet polarity * engagement ratio (unknown).
    tweet_mult = grab(r"tweet contribution equals {N} multiplied by", text)
    tweet_polarity = grab(r"average tweet polarity {N}", text)

    # Sentence 4: total = news + tweet  ->  solve for engagement ratio.
    tweet_needed = total_target - news_contribution
    engagement_ratio = tweet_needed / (tweet_mult * tweet_polarity)

    return {
        "final": Fraction(engagement_ratio),
        "slots": {"news_score_checkpoint": Fraction(news_contribution)},
    }
