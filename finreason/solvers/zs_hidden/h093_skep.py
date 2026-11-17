"""h093 -- sentiment model: solve for the unknown tweet engagement ratio.

Structure (identical across the 3 instances, numbers differ):
    total      = news_contribution + tweet_contribution
    news       = n_news  * news_polarity  * influence_factor        (all given)
    tweet      = n_tweet * tweet_polarity * engagement_ratio        (engagement unknown)
    engagement = (total - news) / (n_tweet * tweet_polarity)

AMBIGUITY HUNT (resolved with textual evidence):
1. "X multiplied by average news polarity P and influence factor I" -- is this
   X*P*I (triple product) or X*(P+I)?  "multiplied by ... and ..." lists two
   multiplicands; the tweet sentence has the exact same shape with "and an
   unknown engagement ratio", and the unit of the answer is "ratio", i.e. a
   multiplicative scaling factor.  Triple product.  (An additive reading would
   make "engagement ratio" an additive score term, which contradicts "ratio".)
2. Is "total score" possibly a percent / scaled quantity?  No: "total score of
   9.69903" is a plain number, contributions are plain numbers; answer unit is
   "ratio" and checkpoint unit "dimensionless" -- no /100 anywhere.
3. Checkpoint "weighted news contribution": the news contribution itself
   (count * polarity * influence), dimensionless, unrounded.  "Weighted" refers
   to it being weighted by count and influence; it is NOT news/total or a share.
4. Influence factor appears as a rational (1198889/6000000) in one instance and
   as decimals (2.0208964, 1.50989142) in the others; polarities are rationals
   (2/13, 31/17).  finreason.nums NUMBER handles both forms exactly.
5. Rounding: "use exact arithmetic through all intermediate steps, round only
   the final value" -- no intermediate rounding; return exact Fractions and let
   the framework round half-up to 6 dp.
6. Sign / floor: no clamping is described; if total < news the engagement would
   be negative and is reported as such (does not occur in these 3 instances but
   the formula is applied verbatim either way).
7. Order of operations: tweet = count * polarity * engagement, so engagement
   divides out BOTH count and polarity (not just the count).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h093"


def solve(text: str, q: dict) -> dict:
    total = grab(r"total score of {N}", text)

    n_news = grab(r"news contribution equals {N} multiplied by", text)
    news_pol = grab(r"average news polarity {N}", text)
    influence = grab(r"influence factor {N}", text)

    n_tweet = grab(r"tweet contribution equals {N} multiplied by", text)
    tweet_pol = grab(r"average tweet polarity {N}", text)

    news = n_news * news_pol * influence
    tweet_needed = total - news
    engagement = tweet_needed / (n_tweet * tweet_pol)

    return {
        "final": Fraction(engagement),
        "slots": {"news_score_checkpoint": Fraction(news)},
    }
