"""h026 -- tweet/news sentiment aggregate with sequential moderation of the tweet signal.

FINANCE MODEL (written before coding)
-------------------------------------
Quantity: a dimensionless composite sentiment signal S, classified into Bullish / Neutral / Bearish.

  tweet_raw      = T * p_t                      (T = scale/count multiplier, p_t = signed average tweet polarity,
                                                 polarity lives on the scenario scale [-1, 1])
  stage retention r = 1 - u                     (u = fraction of the *surviving* signed signal removed at each
                                                 moderation stage; same u every stage; no replenishment)
  after k stages the surviving signal is multiplied by r^k (geometric attrition); here k = 3 so the
  "final retention factor" is (1-u)^3.  The sign of the signal is untouched (r > 0), only magnitude shrinks.
  tweet_retained = tweet_raw * (1-u)^k
  news           = M * p_n * w                  (M = news multiplier, p_n = signed average news polarity,
                                                 w = influence factor, a plain ratio, may be a fraction a/b)
  market         = separate signed dimensionless market signal (added as is, NOT moderated)
  S = tweet_retained + news + market            (exact rational arithmetic, no rounding anywhere)

Classification (exactly as worded):
  Bullish  if S >= bull_threshold               ("at least"  -> non-strict)
  Bearish  if S <= -bear_threshold              ("at most the negative of X" -> S <= -X, non-strict)
  Neutral  otherwise.

Overrides / conventions noted:
  * Percent conversion: none -- u is given as a plain ratio (0.2 means 20 percent removal), not as percent.
  * Bear threshold is given as a positive magnitude ("the negative of 14"), so the cut-off is -14.
  * Checkpoint slot "tweet_retention_factor_checkpoint" is described as "the signed-signal retention factor
    after ONE stage": that is the per-stage retention 1-u (position 1 in the chain, before cubing).
    (Corroboration: instance 1 uses u=0.1999995 so that 1-u = 0.8000005, an exact half-up tie at the
    slot's 6 decimal places -> 0.800001; the cube 0.51200096... would not exercise that tie.)
    The final answer uses the full cube (1-u)^3 anyway.
"""
from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h026"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stages(text: str) -> int:
    m = re.search(r"\(1-u\)\^(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"exactly\s+(\w+)\s+sequential", text)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        return int(w)
    raise ValueError("cannot determine number of moderation stages")


def solve(text: str, q: dict) -> dict:
    # --- inputs ---------------------------------------------------------------------------------
    tweet_mult = grab(r"raw tweet signal is {N} times signed average polarity", text)
    tweet_pol = grab(r"raw tweet signal is [^ ]+ times signed average polarity {N}", text)
    u = grab(r"ratio u={N} of the surviving", text)
    k = _stages(text)

    news_mult = grab(r"news contribution is {N} times signed average polarity", text)
    news_pol = grab(r"news contribution is [^ ]+ times signed average polarity {N} times influence", text)
    influence = grab(r"times influence factor {N}", text)

    market = grab(r"separate signed dimensionless market signal {N}", text)

    bull = grab(r"Bullish when it is at least {N}", text)
    bear = grab(r"Bearish when it is at most the negative of {N}", text)

    # --- model ----------------------------------------------------------------------------------
    stage_retention = 1 - u                       # per-stage retention factor (checkpoint)
    total_retention = stage_retention ** k        # (1-u)^k
    tweet_raw = tweet_mult * tweet_pol
    tweet_retained = tweet_raw * total_retention
    news = news_mult * news_pol * influence
    aggregate = tweet_retained + news + market

    if aggregate >= bull:
        label = "Bullish"
    elif aggregate <= -bear:
        label = "Bearish"
    else:
        label = "Neutral"

    return {
        "final": label,
        "slots": {"tweet_retention_factor_checkpoint": stage_retention},
    }
