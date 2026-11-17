from fractions import Fraction
from finreason.nums import grab, F

TEMPLATE_ID = "h093"


def solve(text: str, q: dict) -> dict:
    target = grab(r"total score of {N}", text)
    n_mult = grab(r"news contribution equals {N} multiplied", text)
    n_pol = grab(r"average news polarity {N}", text)
    n_inf = grab(r"influence factor {N}", text)
    t_mult = grab(r"tweet contribution equals {N} multiplied", text)
    t_pol = grab(r"average tweet polarity {N}", text)

    news = n_mult * n_pol * n_inf
    ratio = (target - news) / (t_mult * t_pol)
    return {"final": ratio, "slots": {"news_score_checkpoint": news}}
