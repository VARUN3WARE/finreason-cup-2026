"""Solver for hidden cluster h026 -- moderated tweet signal + news + market signal -> sentiment class.

Structure (identical across the 3 instances, numbers/branches differ):
    raw_tweet      = A * P_tweet                       ("raw tweet signal is A times signed average polarity P")
    retained_tweet = raw_tweet * (1-u)^k               (k sequential stages, each removes ratio u -> retains 1-u)
    news           = B * P_news * I                    ("B times signed average polarity P times influence factor I")
    aggregate      = retained_tweet + news + M         (M = separate signed dimensionless market signal)
    final          = Bullish  if aggregate >= T_bull
                     Bearish  if aggregate <= -T_bear
                     Neutral  otherwise

AMBIGUITIES CONSIDERED AND RESOLUTIONS (with textual evidence):

1. Which quantity is the checkpoint "signed-signal retention factor after one stage"?
   Candidates: 1-u, (1-u)^3, u, or the retained signal value A*P*(1-u).
   -> 1-u.  Text: "each stage retains 1-u and the final retention factor is (1-u)^3"; the slot says
      "after ONE stage" and its unit is "ratio" (a factor, not a signal amount).  Instance 1 uses
      u=0.1999995 so 1-u = 0.8000005 sits exactly on the 6-dp half-up boundary (-> 0.800001); that boundary
      test only makes sense for 1-u.  Returned UNROUNDED; the framework applies half-up/6dp.

2. Is the rounded checkpoint (0.800001) fed back into the aggregate?
   -> No.  Text says "Classify the EXACT aggregate"; nothing says a rounded factor is used downstream.
      The exact (1-u)^3 is used in the chain.

3. Number of stages / exponent.
   -> Parsed from "(1-u)^k" in the text (k=3 in all instances); fallback to the spelled count ("three")
      and finally 3.  "no replenishment between stages" just confirms plain compounding of retention.

4. Removal ratio u: "ratio u=0.1999995 of the surviving signed signal is removed" -> u is a plain ratio
   (not a percent), applied multiplicatively to the surviving (already-reduced) signal each stage, hence (1-u)^k.

5. Signs.  Polarities are signed (-1..1 scale), the market signal is signed, and the removal acts on the
   "signed signal", so a negative raw tweet signal is shrunk toward zero (multiplied by (1-u)^k), not made
   more negative.  No clipping of polarity to [-1,1] is applied: the scale sentence is descriptive only and
   every given polarity already lies inside it.

6. Influence factor applies to the NEWS contribution only ("news contribution is B times ... times influence
   factor I"); the tweet contribution has no influence factor.

7. Thresholds: "at least T" -> aggregate >= T (non-strict); "at most the negative of T" -> aggregate <= -T
   (non-strict, T negated as worded).  Bullish is tested first (listed first); with positive T's the two
   conditions are mutually exclusive anyway.  Otherwise Neutral.

8. All parsing anchors on surrounding words; rationals like -5/9 and 7/11 and long decimals like
   -19.406462199848874901875 are handled exactly by finreason.nums (Fraction).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h026"

_WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stage_count(text: str) -> int:
    """Exponent k of (1-u)^k; fallback to the spelled stage count; final fallback 3."""
    try:
        k = grab(r"\(\s*1\s*-\s*u\s*\)\s*\^\s*{N}", text)
        if k.denominator == 1 and k > 0:
            return int(k)
    except ValueError:
        pass
    m = re.search(r"exactly\s+(\w+)\s+sequential", text)
    if m:
        w = m.group(1).lower()
        if w in _WORD_NUMS:
            return _WORD_NUMS[w]
        if w.isdigit():
            return int(w)
    return 3


def solve(text: str, q: dict) -> dict:
    # --- tweet side
    tweet_mult = grab(r"raw tweet signal is {N} times signed average polarity", text)
    tweet_pol = grab(r"raw tweet signal is (?:{N}) times signed average polarity {N}", text, group=2)
    u = grab(r"ratio u\s*=\s*{N}", text)
    k = _stage_count(text)

    one_stage_retention = Fraction(1) - u            # checkpoint: retention factor after one stage
    retention = one_stage_retention ** k             # exact integer power
    raw_tweet = tweet_mult * tweet_pol
    retained_tweet = raw_tweet * retention

    # --- news side
    news_mult = grab(r"news contribution is {N} times signed average polarity", text)
    news_pol = grab(r"news contribution is (?:{N}) times signed average polarity {N}", text, group=2)
    influence = grab(r"times influence factor {N}", text)
    news = news_mult * news_pol * influence

    # --- market signal
    market = grab(r"market signal {N}", text)

    aggregate = retained_tweet + news + market

    # --- classification thresholds
    bull_t = grab(r"Bullish when it is at least {N}", text)
    bear_t_raw = grab(r"Bearish when it is at most the negative of {N}", text)
    bear_t = -bear_t_raw

    if aggregate >= bull_t:
        final = "Bullish"
    elif aggregate <= bear_t:
        final = "Bearish"
    else:
        final = "Neutral"

    return {
        "final": final,
        "slots": {
            "tweet_retention_factor_checkpoint": one_stage_retention,
        },
    }
