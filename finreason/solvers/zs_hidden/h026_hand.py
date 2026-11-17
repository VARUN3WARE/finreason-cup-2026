from fractions import Fraction
import re

from finreason.nums import grab, grab_all, NUMBER

TEMPLATE_ID = "h026"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _stage_count(text: str) -> int:
    m = re.search(r"exactly (\w+) sequential moderation stages", text)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        if w.isdigit():
            return int(w)
    m = re.search(r"\(1-u\)\^(\d+)", text)
    return int(m.group(1))


def _threshold(label: str, cmp_word: str, text: str) -> Fraction:
    # e.g. "Bearish when it is at most the negative of 1"
    rx = label + r" when it is " + cmp_word + r" (the negative of )?(" + NUMBER + r")"
    m = re.search(rx, text)
    if m is None:
        raise ValueError(f"threshold for {label} not found")
    v = Fraction(m.group(2).replace(",", ""))
    if m.group(1):
        v = -v
    return v


def solve(text: str, q: dict) -> dict:
    t_scale, t_pol = grab_all(r"raw tweet signal is {N} times signed average polarity {N}", text)
    u = grab(r"ratio u\s*=\s*{N}", text)
    k = _stage_count(text)

    retain_one = 1 - u
    retained_tweet = t_scale * t_pol * retain_one ** k

    n_scale, n_pol, n_inf = grab_all(
        r"news contribution is {N} times signed average polarity {N} times influence factor {N}", text)
    news = n_scale * n_pol * n_inf

    market = grab(r"signed dimensionless market signal {N}", text)

    agg = retained_tweet + news + market

    bull = _threshold("Bullish", "at least", text)
    bear = _threshold("Bearish", "at most", text)

    if agg >= bull:
        final = "Bullish"
    elif agg <= bear:
        final = "Bearish"
    else:
        final = "Neutral"

    return {"final": final, "slots": {"tweet_retention_factor_checkpoint": retain_one}}
