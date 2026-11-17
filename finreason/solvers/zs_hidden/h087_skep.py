"""h087 -- share of total expected gross integration benefit attributable to the
incremental joint (both-succeed) benefit of two independent post-merger initiatives.

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED (textual evidence in brackets):

1. What is each "expected standalone benefit"?
   -> p_i * amount_i, using the MARGINAL success probability and the standalone
      contribution ["succeeds with marginal probability p and contributes X USD
      millions whenever it succeeds"]. "Standalone" excludes the joint benefit
      ["incremental joint benefit ... beyond the two standalone benefits"].
      Checkpoint 1 = p_c * C (cost-synergy), checkpoint 2 = p_r * R (revenue-synergy),
      both in USD millions (the amounts are already given in USD millions).

2. Probability that the joint benefit materialises.
   -> It is paid only "If both succeed"; outcomes are independent ["Assume the two
      initiative outcomes are independent"], so P(both) = p_c * p_r exactly.
      Expected joint benefit = p_c * p_r * J.

3. What is "total expected gross integration benefit"?
   -> The expectation of everything the integration produces: E[cost standalone]
      + E[revenue standalone] + E[incremental joint]. "Gross" = before any costs
      (no costs are mentioned, so nothing is subtracted). The joint benefit is
      "incremental ... beyond the two standalone benefits", i.e. additive, not a
      replacement for the both-succeed payoff.

4. What is "attributable specifically to that incremental joint benefit"?
   -> Only the expected incremental amount p_c*p_r*J -- NOT the whole both-succeed
      scenario payoff (C + R + J). "Specifically" and "that incremental joint
      benefit" single out J alone.

5. Units of the final answer.
   -> "Compute the percentage" and answer unit `percent`: return 100 * share
      (e.g. 13.44 means 13.44%). Checkpoints stay in USD millions (unit usd_million).

6. Rounding.
   -> None inside the computation ["Carry exact probabilities and amounts through
      the calculation"; answer format: round only the final value]. All returned
      values are unrounded Fractions; the framework applies half-up rounding.

7. Probability format.
   -> Given as decimals (0.4, 0.51). Defensively, if a probability is written with
      "percent"/"%" right after it, it is divided by 100.

8. Which sentence feeds which initiative.
   -> Regexes are anchored on "cost-synergy initiative" / "revenue-synergy
      initiative" so sentence order does not matter; "cost synergy" (no hyphen) is
      also accepted.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h087"


def _initiative(text: str, kind: str) -> tuple[Fraction, Fraction]:
    """Return (success probability as a plain ratio, standalone amount in USD millions)."""
    rx = (
        rf"{kind}[-\s]synergy initiative succeeds with (?:a |the )?marginal "
        rf"(?:success )?probability(?: of)? ({NUMBER})\s*(percent|%)?"
        rf"\s*(?:,|and)?\s*contributes(?: an? benefit of)? ({NUMBER})\s*USD million"
    )
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"could not parse the {kind}-synergy initiative sentence")
    p = F(m.group(1))
    if m.group(2):
        p = p / 100
    amount = F(m.group(3))
    return p, amount


def _joint(text: str) -> Fraction:
    rx = rf"incremental joint benefit(?: of)? ({NUMBER})\s*USD million"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError("could not parse the incremental joint benefit")
    return F(m.group(1))


def solve(text: str, q: dict) -> dict:
    p_c, amt_c = _initiative(text, "cost")
    p_r, amt_r = _initiative(text, "revenue")
    joint = _joint(text)

    # Checkpoints: expected standalone benefits (marginal probability x standalone amount).
    exp_cost = p_c * amt_c
    exp_rev = p_r * amt_r

    # Joint benefit is earned only when both succeed; independence -> product of marginals.
    p_both = p_c * p_r
    exp_joint = p_both * joint

    total = exp_cost + exp_rev + exp_joint
    if total == 0:
        raise ValueError("total expected gross integration benefit is zero; share undefined")

    share_pct = exp_joint / total * 100

    return {
        "final": share_pct,
        "slots": {
            "expected_cost_benefit_checkpoint": exp_cost,
            "expected_revenue_benefit_checkpoint": exp_rev,
        },
    }
