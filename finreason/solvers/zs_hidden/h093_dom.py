# FINANCE MODEL (h093): solving for a required engagement ratio in a two-channel sentiment score.
#
#   total   = news_contribution + tweet_contribution          (given: "sum of these two contributions")
#   news    = W_news  * pol_news  * influence                 (all three given; "multiplied by")
#   tweet   = W_tweet * pol_tweet * engagement                (engagement is the unknown)
#   =>  engagement = (total - news) / (W_tweet * pol_tweet)
#
# Inputs: W_news / W_tweet are the leading integer weights ("19 multiplied by ...", "14 multiplied by ..."),
#   pol_* are the average polarities (rationals), influence is the influence factor (decimal or rational),
#   total is the target total score.
# No overrides of standard conventions: plain multiplication, plain sum, no rounding inside the chain.
# Checkpoint news_score_checkpoint = the "weighted news contribution" = news (dimensionless), unrounded here;
#   the framework applies half-up rounding to 6 dp. Final answer = engagement ratio (ratio unit), unrounded.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h093"


def solve(text: str, q: dict) -> dict:
    target = grab(r"reach a total score of {N}", text)
    w_news, pol_news, influence = grab_all(
        r"news contribution equals {N} multiplied by average news polarity {N} and influence factor {N}", text)
    w_tweet, pol_tweet = grab_all(
        r"tweet contribution equals {N} multiplied by average tweet polarity {N} and an unknown", text)

    news = w_news * pol_news * influence
    denom = w_tweet * pol_tweet
    engagement = (target - news) / denom

    return {"final": engagement, "slots": {"news_score_checkpoint": news}}
