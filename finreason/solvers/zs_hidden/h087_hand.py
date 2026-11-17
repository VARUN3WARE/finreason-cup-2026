"""h087: share of total expected gross integration benefit due to the joint (both-succeed) benefit.

E[cost]  = p_c * B_c
E[rev]   = p_r * B_r
E[joint] = p_c * p_r * J        (independent outcomes -> P(both) = p_c * p_r)
answer   = E[joint] / (E[cost] + E[rev] + E[joint]) * 100   (percent)
"""
from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h087"


def _prob(label: str, text: str) -> Fraction:
    rx = label + r" initiative succeeds with (?:marginal )?probability (" + NUMBER + r")(\s*(?:%|percent))?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"probability for {label} not found")
    p = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        p /= 100
    return p


def _amount(label: str, text: str) -> Fraction:
    return grab(label + r" initiative succeeds with .*?contributes (?:USD )?{N}", text)


def solve(text: str, q: dict) -> dict:
    p_c = _prob("cost-synergy", text)
    b_c = _amount("cost-synergy", text)
    p_r = _prob("revenue-synergy", text)
    b_r = _amount("revenue-synergy", text)
    joint = grab(r"incremental joint benefit (?:of )?(?:USD )?{N}", text)

    e_cost = p_c * b_c
    e_rev = p_r * b_r
    p_both = p_c * p_r          # independence stated in the text
    e_joint = p_both * joint
    total = e_cost + e_rev + e_joint

    share_pct = e_joint / total * 100
    return {
        "final": share_pct,
        "slots": {
            "expected_cost_benefit_checkpoint": e_cost,
            "expected_revenue_benefit_checkpoint": e_rev,
        },
    }
