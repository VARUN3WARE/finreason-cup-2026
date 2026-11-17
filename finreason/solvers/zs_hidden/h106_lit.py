"""h106 -- order of a modernization capex and a true asset reduction over two equal periods.

LITERAL TRANSCRIPTION: every sentence of the question becomes a named variable / rule below, in the
order the text gives them.  Exact Fractions throughout; nothing is rounded inside the computation.

Final = 100 * (reduction-first normalized factor - capex-first normalized factor), where for each order
    normalized factor = [ mean(two period run-rate sales) / mean(two period asset bases) ] / (S0 / A0)
and S0 / A0 is the common pre-action turnover (A0 = retained base + true reduction).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h106"

SLOT_SALES_FACTOR = "combined_sales_effect_checkpoint"
SLOT_P2_ASSETS = "shared_second_period_asset_base_checkpoint"


def _effect_size(pattern: str, text: str) -> Fraction:
    """Sales-effect size: a bare number (e.g. 0.5) is a decimal fraction; 'N percent' / 'N%' is a percentage."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"(\s*(?:%|percent\b))?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    if m.group(2):
        value = value / 100
    return value


def _mean(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


def solve(text: str, q: dict) -> dict:
    # S1 "A company is comparing the order of two actions across two equal-length operating periods."
    #    -> two orders (capex-first, reduction-first); two periods of equal length, so the per-period
    #       run-rate amounts are weighted equally.
    n_periods = 2

    # S2 "{R} is the net total-asset base that remains after a true reduction of {D}, and {C} is the
    #     modernization program's net capitalized addition to total assets."
    retained_base = grab(r"{N} is the net total-asset base that remains after", text)
    true_reduction = grab(r"remains after a true reduction of {N}", text)
    capex_addition = grab(r"{N} is the modernization program's net capitalized addition to total assets", text)
    # the base that remains after the (true) reduction is the pre-action base less the reduction
    pre_action_base = retained_base + true_reduction

    # S3 "Modernization raises run-rate net sales by {g}, while the reduction lowers run-rate net sales by {l};
    #     each effect begins at its action date, persists, and the two sales effects compound."
    modernization_uplift = _effect_size(r"Modernization raises run-rate net sales by {N}", text)
    reduction_drag = _effect_size(r"the reduction lowers run-rate net sales by {N}", text)
    modernization_factor = 1 + modernization_uplift
    reduction_factor = 1 - reduction_drag
    # compounding: once both actions have occurred, sales = S0 * (1 + g) * (1 - l)
    combined_sales_factor = modernization_factor * reduction_factor

    # Baseline (pre-action) run-rate sales S0 is not given; it cancels on normalization, so take S0 = 1.
    baseline_sales = Fraction(1)
    baseline_turnover = baseline_sales / pre_action_base  # "the common pre-action turnover"

    # S4 "In the capex-first order, period-one assets equal the pre-action base plus the addition and
    #     period-two assets equal the retained base plus the addition."
    #    -> modernization at the start of period one, reduction at the start of period two; each sales
    #       effect begins at its action date and persists.
    capex_first_assets = [pre_action_base + capex_addition, retained_base + capex_addition]
    capex_first_sales = [
        baseline_sales * modernization_factor,                     # period one: modernization only
        baseline_sales * modernization_factor * reduction_factor,  # period two: both, compounded
    ]

    # S5 "In the reduction-first order, period-one assets equal the retained base and period-two assets equal
    #     the same final retained-plus-addition base."
    #    -> reduction at the start of period one, modernization at the start of period two.
    reduction_first_assets = [retained_base, retained_base + capex_addition]
    reduction_first_sales = [
        baseline_sales * reduction_factor,                         # period one: reduction only
        baseline_sales * reduction_factor * modernization_factor,  # period two: both, compounded
    ]
    assert len(capex_first_assets) == len(reduction_first_assets) == n_periods

    # S6 "For each order, compute the arithmetic mean of the two period run-rate sales amounts divided by the
    #     arithmetic mean of the two period asset bases, equivalently their sums divided by their sums, and
    #     normalize this turnover by the common pre-action turnover."
    capex_first_turnover = _mean(capex_first_sales) / _mean(capex_first_assets)
    reduction_first_turnover = _mean(reduction_first_sales) / _mean(reduction_first_assets)
    assert capex_first_turnover == sum(capex_first_sales) / sum(capex_first_assets)
    assert reduction_first_turnover == sum(reduction_first_sales) / sum(reduction_first_assets)
    capex_first_normalized = capex_first_turnover / baseline_turnover
    reduction_first_normalized = reduction_first_turnover / baseline_turnover

    # S7 "What is the reduction-first normalized factor minus the capex-first normalized factor, expressed as a
    #     percentage of baseline turnover?"  (normalized factors are multiples of baseline turnover -> x100)
    final = (reduction_first_normalized - capex_first_normalized) * 100

    # Checkpoints: the period-two state is common to both orders (both actions done).
    common_p2_sales_factor = capex_first_sales[1] / baseline_sales
    assert common_p2_sales_factor == reduction_first_sales[1] / baseline_sales == combined_sales_factor
    common_p2_assets = capex_first_assets[1]
    assert common_p2_assets == reduction_first_assets[1] == retained_base + capex_addition

    return {
        "final": final,
        "slots": {
            SLOT_SALES_FACTOR: common_p2_sales_factor,  # multiple of baseline run-rate sales
            SLOT_P2_ASSETS: common_p2_assets,           # usd
        },
    }
