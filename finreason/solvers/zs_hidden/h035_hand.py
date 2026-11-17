"""h035: crypto price shock, severe/mild policy branch on loss ratio, then support uplift and deduction."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h035"


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"starts at {N} USD per token", text)
    loss = grab(r"loses fraction {N} of its price", text)

    # Threshold comparison as worded ("at least" -> >=; defensive support for strict wording).
    if grab_ok(r"loss ratio is at least {N}", text):
        thr = grab(r"loss ratio is at least {N}", text)
        severe = loss >= thr
    elif grab_ok(r"loss ratio is (?:strictly )?(?:greater|more) than {N}", text):
        thr = grab(r"loss ratio is (?:strictly )?(?:greater|more) than {N}", text)
        severe = loss > thr
    else:
        thr = grab(r"loss ratio is[^0-9]*{N}", text)
        severe = loss >= thr

    sev_support = grab(r"severe policy increases the post-shock price by support ratio {N}", text)
    sev_deduct = grab(r"severe policy increases the post-shock price by support ratio [^ ]+ and then deducts {N} USD", text)
    mild_support = grab(r"mild policy increases it by support ratio {N}", text)
    mild_deduct = grab(r"mild policy increases it by support ratio [^ ]+ and then deducts {N} USD", text)

    retention = 1 - loss
    post = p0 * retention

    if severe:
        net = post * (1 + sev_support) - sev_deduct
    else:
        net = post * (1 + mild_support) - mild_deduct

    return {"final": Fraction(net), "slots": {"post_shock_retention_checkpoint": Fraction(retention)}}


def grab_ok(pattern: str, text: str) -> bool:
    try:
        grab(pattern, text)
        return True
    except ValueError:
        return False
