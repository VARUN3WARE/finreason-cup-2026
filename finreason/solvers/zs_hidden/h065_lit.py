"""h065 -- literal transcription: TWR (chain-linked, two subperiods around a mid-period
contribution, terminal distribution) minus standard Modified Dietz, in signed percentage points."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h065"


def solve(text: str, q: dict) -> dict:
    # "An investment account begins a measurement period at value B."
    begin_value = grab(r"begins a measurement period at value {N}", text)
    # "Immediately before a contribution of C is added after t of the period has elapsed,
    #  the account value is V_pre."
    contribution = grab(r"contribution of {N} is added", text)
    elapsed = grab(r"is added after {N} of the period has elapsed", text)
    value_before_contribution = grab(r"has elapsed, the account value is {N}", text)
    # "At period end, the post-distribution account value is E and a terminal cash
    #  distribution of D is paid at that same time; the ending value excludes that distribution."
    end_value_post_dist = grab(r"post-distribution account value is {N}", text)
    distribution = grab(r"terminal cash distribution of {N}", text)
    # "There are no other external cash flows or valuation changes at the contribution instant."
    value_after_contribution = value_before_contribution + contribution

    # Chain-linked TWR from the pre- and post-contribution subperiods.
    # Subperiod 1: begin -> immediately before contribution.
    r1 = value_before_contribution / begin_value - 1
    # Subperiod 2: just after contribution -> period end; the terminal distribution is
    # paid out of the account at period end, so the pre-distribution end value is E + D.
    r2 = (end_value_post_dist + distribution) / value_after_contribution - 1
    twr = (1 + r1) * (1 + r2) - 1

    # Standard Modified Dietz with the contribution's remaining-period weight (1 - t);
    # the terminal distribution occurs at period end -> weight 0.
    w_contribution = 1 - elapsed
    w_distribution = Fraction(0)
    net_flows = contribution - distribution
    md_num = end_value_post_dist - begin_value - net_flows
    md_den = begin_value + w_contribution * contribution - w_distribution * distribution
    md = md_num / md_den

    final = (twr - md) * 100  # signed percentage points
    return {"final": final, "slots": {"period_one_return_checkpoint": r1}}
