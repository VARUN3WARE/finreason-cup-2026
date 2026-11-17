"""h025: two-scenario project NPV; minimum gross terminal salvage meeting an
expected-NPV floor and a stressed-scenario NPV floor.

Model (per scenario s with effective annual rate r_s):
    NPV_s(S) = -C0 + I/(1+r_s)^t1 + (S - K)/(1+r_s)^t2
Expected NPV = p*NPV_stress + (1-p)*NPV_normal  (conditional NPVs carry no probabilities).
Both constraints are increasing in S, so the minimum salvage is the max of the two
break-even salvages.
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h025"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate; treat it as percent only if the text says 'percent' right after it."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"(?P<pct>\s*(?:percent|%))?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group("pct"):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    c0 = grab(r"costs {N} USD now", text)
    interim = grab(r"interim cash flow of {N} USD", text)
    t1 = int(grab(r"interim cash flow of {N} USD after {N} whole years", text, 2))
    cleanup = grab(r"cleanup cost {N} USD", text)
    t2 = int(grab(r"cleanup cost {N} USD together with salvage after {N} whole years", text, 2))

    p_s = grab(r"stress scenario has probability {N}", text)
    r_s = _rate(r"stress scenario has probability [^ ]+ and effective annual discount rate {N}", text)
    if re.search(r"normal scenario has probability one minus", text):
        p_n = 1 - p_s
    else:
        p_n = grab(r"normal scenario has probability {N}", text)
    r_n = _rate(r"normal scenario has probability .*? and effective annual discount rate {N}", text)

    e_min = grab(r"expected NPV at least {N} USD", text)
    s_min = grab(r"stressed-scenario NPV at least {N} USD", text)

    d_s1 = (1 + r_s) ** t1
    d_n1 = (1 + r_n) ** t1
    d_s2 = (1 + r_s) ** t2
    d_n2 = (1 + r_n) ** t2

    pv_int_n = interim / d_n1
    pv_int_s = interim / d_s1

    # Stressed-scenario floor: -c0 + pv_int_s + (S - K)/d_s2 >= s_min
    sal_stress = cleanup + (s_min + c0 - pv_int_s) * d_s2
    # Expected-NPV floor: p_s*NPV_s + p_n*NPV_n >= e_min
    coef = p_s / d_s2 + p_n / d_n2
    base = p_s * (-c0 + pv_int_s) + p_n * (-c0 + pv_int_n)
    sal_exp = cleanup + (e_min - base) / coef

    salvage = max(sal_stress, sal_exp)

    return {
        "final": salvage,
        "slots": {
            "normal_interim_present_value_checkpoint": pv_int_n,
            "stressed_interim_present_value_checkpoint": pv_int_s,
        },
    }
