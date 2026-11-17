"""h106: order of a capex (modernization) action and an asset reduction across two periods.

Structure (from the question text):
  * R   = net total-asset base that remains after the true reduction (retained base)
  * red = the true reduction, so the pre-action base A0 = R + red
  * add = modernization's net capitalized addition to total assets
  * modernization changes run-rate sales by +u, the reduction by -d (decimal fractions);
    each effect starts at its action date, persists, and the two effects compound.

  Capex-first:     period-1 assets A0 + add, sales factor (1+u)
                   period-2 assets R + add,  sales factor (1+u)(1-d)
  Reduction-first: period-1 assets R,        sales factor (1-d)
                   period-2 assets R + add,  sales factor (1-d)(1+u)

  Turnover of an order = (sum of period sales) / (sum of period asset bases)
  (= mean / mean); normalized by the pre-action turnover S0 / A0, so the unknown
  S0 cancels:  factor = (sum of sales factors) * A0 / (sum of asset bases).

  Final = (reduction-first factor - capex-first factor) * 100, in percent of baseline turnover.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h106"


def _rate(verb_pattern: str, text: str) -> Fraction:
    """Signed relative sales change following ``verb_pattern`` (e.g. 'Modernization ...').

    A bare decimal is a fraction (0.5 = +50%); a number tagged 'percent'/'%' is divided by 100.
    The verb (raises/increases vs lowers/reduces/decreases/cuts) sets the sign.
    """
    rx = (
        verb_pattern
        + r"\s+(raises|increases|lifts|boosts|lowers|reduces|decreases|cuts)\s+run-rate net sales by\s+("
        + NUMBER
        + r")\s*(percent|%)?"
    )
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"sales effect not found for {verb_pattern!r}")
    value = F(m.group(2))
    if m.group(3):
        value = value / 100
    if m.group(1).lower() in ("lowers", "reduces", "decreases", "cuts"):
        value = -value
    return value


def solve(text: str, q: dict) -> dict:
    retained, reduction = grab_all(
        r"{N} is the net total-asset base that remains after a true reduction of {N}", text
    )
    addition = grab(r"{N} is the modernization program's net capitalized addition", text)

    capex_effect = _rate(r"Modernization", text)  # e.g. +1/2
    reduction_effect = _rate(r"the reduction", text)  # e.g. -1/5

    pre_base = retained + reduction  # A0

    capex_factor = 1 + capex_effect
    reduction_factor = 1 + reduction_effect
    combined_factor = capex_factor * reduction_factor  # common period-two sales factor

    final_base = retained + addition  # common period-two asset base

    # Capex-first order
    cf_sales = capex_factor + combined_factor
    cf_assets = (pre_base + addition) + final_base
    cf_norm = cf_sales / cf_assets * pre_base

    # Reduction-first order
    rf_sales = reduction_factor + combined_factor
    rf_assets = retained + final_base
    rf_norm = rf_sales / rf_assets * pre_base

    final = (rf_norm - cf_norm) * 100

    return {
        "final": final,
        "slots": {
            "combined_sales_effect_checkpoint": combined_factor,
            "shared_second_period_asset_base_checkpoint": final_base,
        },
    }
