"""h019 -- maximum common stress activity across capital, leverage and liquidity constraints.

Literal transcription of the question text, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h019"


def solve(text: str, q: dict) -> dict:
    # "A bank begins with eligible capital E, Tier 1 capital T1, risk-weighted assets RWA,
    #  total exposure X, high-quality liquid assets HQLA, and total net cash outflows NCO,
    #  all in USD millions."
    starting_eligible_capital = grab(r"begins with eligible capital {N}", text)
    tier_one_capital = grab(r"Tier 1 capital {N},", text)
    risk_weighted_assets = grab(r"risk-weighted assets {N},", text)
    total_exposure = grab(r"total exposure {N},", text)
    high_quality_liquid_assets = grab(r"high-quality liquid assets {N},", text)
    total_net_cash_outflows = grab(r"total net cash outflows {N},", text)

    # "The scenario supplies minimum capital ratio a, capital buffer ratio b,
    #  minimum leverage ratio c, and minimum liquidity ratio d as decimal ratios."
    minimum_capital_ratio = grab(r"minimum capital ratio {N}", text)
    capital_buffer_ratio = grab(r"capital buffer ratio {N}", text)
    minimum_leverage_ratio = grab(r"minimum leverage ratio {N}", text)
    minimum_liquidity_ratio = grab(r"minimum liquidity ratio {N}", text)

    # "One dimensionless common stress activity x decreases eligible capital by p*x and
    #  Tier 1 capital by q*x, while increasing risk-weighted assets by r*x, exposure by s*x,
    #  reducing HQLA by t*x, and increasing net cash outflows by u*x."
    # "Each stress coefficient is the USD-million adverse change caused by one unit of x."
    eligible_capital_loss_per_stress_unit = grab(r"decreases eligible capital by {N}\s*\*\s*x", text)
    tier_one_capital_loss_per_stress_unit = grab(r"Tier 1 capital by {N}\s*\*\s*x", text)
    risk_weighted_assets_increase_per_stress_unit = grab(
        r"increasing risk-weighted assets by {N}\s*\*\s*x", text)
    total_exposure_increase_per_stress_unit = grab(r"exposure by {N}\s*\*\s*x", text)
    hqla_loss_per_stress_unit = grab(r"reducing HQLA by {N}\s*\*\s*x", text)
    net_cash_outflows_increase_per_stress_unit = grab(
        r"increasing net cash outflows by {N}\s*\*\s*x", text)

    # "Add the minimum capital ratio and buffer ratio to obtain k."
    k = minimum_capital_ratio + capital_buffer_ratio

    # "Solve exactly for the positive x at which each constraint first binds:" (formulas verbatim)
    capital_capacity = (
        (starting_eligible_capital - k * risk_weighted_assets)
        / (eligible_capital_loss_per_stress_unit + k * risk_weighted_assets_increase_per_stress_unit)
    )
    leverage_capacity = (
        (tier_one_capital - minimum_leverage_ratio * total_exposure)
        / (tier_one_capital_loss_per_stress_unit
           + minimum_leverage_ratio * total_exposure_increase_per_stress_unit)
    )
    liquidity_capacity = (
        (high_quality_liquid_assets - minimum_liquidity_ratio * total_net_cash_outflows)
        / (hqla_loss_per_stress_unit
           + minimum_liquidity_ratio * net_cash_outflows_increase_per_stress_unit)
    )

    # "Return the smallest of the three capacities as the maximum common stress activity
    #  allowed by all constraints, in stress multiples using half-up rounding to two decimals."
    maximum_common_stress_activity = min(capital_capacity, leverage_capacity, liquidity_capacity)

    # "Independently report k using half-up rounding to six decimals; use its exact
    #  unrounded value downstream."
    return {
        "final": maximum_common_stress_activity,
        "slots": {"combined_capital_requirement_ratio_checkpoint": k},
    }
