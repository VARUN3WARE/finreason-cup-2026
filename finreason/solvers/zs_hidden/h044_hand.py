"""h044: early vs deferred cleanup NPV difference with escalation, discounting and
a fixed administration outflow at the deferred terminal date.

NPV(early)    = -B (1+g)^te / (1+r)^te
NPV(deferred) = -[B (1+g)^td + A] / (1+r)^td        (A paid only at the deferred terminal date)
final         = NPV(deferred) - NPV(early)          (signed; positive favours deferral)
slot 1        = (1+g)^te                            (cumulative escalation factor to early date)
slot 2        = 1 / (1+r)^td                        (cumulative discount factor to deferred date)
"""

import re
from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "h044"


def _rate(pattern: str, text: str) -> Fraction:
    """Parse a rate stated as a decimal ratio; tolerate an explicit percent/% suffix."""
    v = grab(pattern, text)
    rx = pattern.replace("{N}", r"(?:-?\d[\d,]*(?:\.\d+)?(?:/\d+)?)")
    m = re.search(rx + r"\s*(%|percent)", text, flags=re.S)
    return v / 100 if m else v


def _pow(base: Fraction, e: Fraction) -> Fraction:
    return real_pow(base, Fraction(e))


def solve(text: str, q: dict) -> dict:
    base = grab(r"base cleanup estimate is (?:USD )?{N}", text)
    g = _rate(r"escalation rate (?:of )?{N}", text)
    r = _rate(r"[Dd]iscount all cleanup-related cash flows at the nominal effective annual rate (?:of )?{N}", text)
    t_early = grab(r"early plan pays the resulting cleanup cost at the end of year {N}", text)
    t_def = grab(r"deferred plan pays the resulting cleanup cost at the end of year {N}", text)
    admin = grab(r"administration outflow of (?:USD )?{N}", text)

    # Which plan carries the administration outflow (as worded: the deferred plan,
    # "paid only at that terminal date").
    sentences = re.split(r"(?<=\.)\s+(?=[A-Z])", text)
    admin_sentence = next(s for s in sentences if "administration outflow" in s)
    admin_on_early = "early plan" in admin_sentence and "deferred plan" not in admin_sentence

    growth_early = _pow(1 + g, t_early)
    growth_def = _pow(1 + g, t_def)
    disc_early = 1 / _pow(1 + r, t_early)
    disc_def = 1 / _pow(1 + r, t_def)

    pv_early_out = base * growth_early * disc_early
    pv_def_out = base * growth_def * disc_def
    if admin_on_early:
        pv_early_out += admin * disc_early
    else:
        pv_def_out += admin * disc_def

    npv_early = -pv_early_out
    npv_def = -pv_def_out
    final = npv_def - npv_early

    return {
        "final": final,
        "slots": {
            "early_cleanup_growth_factor_checkpoint": growth_early,
            "terminal_discount_factor_checkpoint": disc_def,
        },
    }
