"""h087 -- share of expected gross integration benefit from the incremental joint (both-succeed) benefit.

Literal transcription of the question:
  - cost-synergy initiative: success prob p_c, contributes B_c whenever it succeeds
  - revenue-synergy initiative: success prob p_r, contributes B_r whenever it succeeds
  - outcomes independent -> P(both succeed) = p_c * p_r
  - if both succeed, incremental joint benefit J beyond the two standalone benefits
  - total expected gross integration benefit = p_c*B_c + p_r*B_r + p_c*p_r*J
  - answer = 100 * (p_c*p_r*J) / total   (percent)
"""
from fractions import Fraction
import re

from finreason.nums import NUMBER

TEMPLATE_ID = "h087"


def _prob(label: str, text: str) -> Fraction:
    """Marginal success probability of the named initiative (decimal, or percent if so worded)."""
    rx = (
        label
        + r"(?:(?!\.\s).)*?probability\s+(?:of\s+)?(" + NUMBER + r")\s*(percent|%)?"
    )
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"probability not found for {label!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2) or v > 1:
        v = v / 100
    return v


def _benefit(label: str, text: str) -> Fraction:
    """Standalone benefit (USD millions) the named initiative contributes whenever it succeeds."""
    rx = label + r"(?:(?!\.\s).)*?contributes\s+(?:USD\s+)?(" + NUMBER + r")"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"benefit not found for {label!r}")
    return Fraction(m.group(1).replace(",", ""))


def _joint(text: str) -> Fraction:
    rx = r"incremental joint benefit\s+(?:of\s+)?(?:USD\s+)?(" + NUMBER + r")"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError("joint benefit not found")
    return Fraction(m.group(1).replace(",", ""))


def solve(text: str, q: dict) -> dict:
    # "The cost-synergy initiative succeeds with marginal probability p_c and contributes B_c USD millions
    #  whenever it succeeds."
    p_c = _prob(r"cost-synergy initiative", text)
    b_c = _benefit(r"cost-synergy initiative", text)
    # "The revenue-synergy initiative succeeds with marginal probability p_r and contributes B_r USD millions
    #  whenever it succeeds."
    p_r = _prob(r"revenue-synergy initiative", text)
    b_r = _benefit(r"revenue-synergy initiative", text)
    # "Assume the two initiative outcomes are independent."
    p_both = p_c * p_r
    # "If both succeed, they also create incremental joint benefit J USD millions beyond the two standalone benefits."
    j = _joint(text)

    # Expected standalone benefits (checkpoints 1 and 2), USD millions.
    exp_cost = p_c * b_c
    exp_rev = p_r * b_r
    # Expected incremental joint benefit.
    exp_joint = p_both * j
    # Total expected gross integration benefit.
    total = exp_cost + exp_rev + exp_joint
    # Percentage attributable specifically to the incremental joint benefit.
    share_pct = exp_joint / total * 100

    return {
        "final": share_pct,
        "slots": {
            "expected_cost_benefit_checkpoint": exp_cost,
            "expected_revenue_benefit_checkpoint": exp_rev,
        },
    }
