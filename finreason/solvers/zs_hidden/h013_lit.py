"""h013 -- managed (advisory charge + fee-bearing rebalance) vs buy-and-hold benchmark.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h013"


def solve(text: str, q: dict) -> dict:
    # "Measure all wealth per 1 USD of original initial notional."
    notional = Fraction(1)

    # "A managed portfolio starts with equity weight w and the complementary bond weight."
    w_eq = grab(r"starts with equity weight {N}", text)
    w_bd = 1 - w_eq
    eq0 = w_eq * notional
    bd0 = w_bd * notional

    # "During period 1, equity and bonds grow by factors gE1 and gB1."
    g_eq1, g_bd1 = grab_all(r"During period 1, equity and bonds grow by factors {N} and {N}", text)
    eq1 = eq0 * g_eq1          # period-1 equity value (checkpoint 1)
    bd1 = bd0 * g_bd1          # period-1 bond value (checkpoint 2), before any midpoint charge

    # "At the midpoint, the advisor deducts a fixed advisory charge equal to c of original
    #  initial notional entirely from the bond side."
    charge = grab(r"advisory charge equal to {N} of original initial notional", text) * notional
    bd_after_charge = bd1 - charge
    wealth_after_charge = eq1 + bd_after_charge

    # "The portfolio is then below its equity target." -- target fraction = starting equity weight.
    target = w_eq

    # "The advisor buys equity and pays transaction fee rate f on the purchase, also from the bond side."
    fee_rate = grab(r"transaction fee rate {N}", text)

    # "Solve the purchase so equity equals its target fraction of wealth after both midpoint charges."
    #   eq1 + P = target * (wealth_after_charge - fee_rate * P)
    #   => P = (target * wealth_after_charge - eq1) / (1 + target * fee_rate)
    purchase = (target * wealth_after_charge - eq1) / (1 + target * fee_rate)
    fee = fee_rate * purchase
    eq_mid = eq1 + purchase
    bd_mid = bd_after_charge - purchase - fee
    wealth_mid = eq_mid + bd_mid
    assert eq_mid == target * wealth_mid

    # "During period 2, equity and bonds grow by factors gE2 and gB2."
    g_eq2, g_bd2 = grab_all(r"During period 2, equity and bonds grow by factors {N} and {N}", text)
    managed_terminal = eq_mid * g_eq2 + bd_mid * g_bd2

    # Fee-free unmanaged buy-and-hold benchmark: original positions through both periods,
    # no midpoint rebalance, neither midpoint charge.
    bench_terminal = eq0 * g_eq1 * g_eq2 + bd0 * g_bd1 * g_bd2

    # "Report managed wealth minus benchmark wealth as a percentage of original initial notional."
    final_pct = (managed_terminal - bench_terminal) / notional * 100

    return {
        "final": final_pct,
        "slots": {
            "period_1_equity_value_checkpoint": eq1,
            "period_1_bond_value_checkpoint": bd1,
        },
    }
