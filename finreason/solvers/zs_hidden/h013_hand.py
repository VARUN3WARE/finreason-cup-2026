"""Hidden cluster h013: managed equity/bond portfolio with a midpoint advisory charge and a
fee-bearing rebalancing purchase, compared with a fee-free buy-and-hold benchmark.

Chain (all wealth per 1 USD of original notional):
  E1 = w * ge1, B1 = (1 - w) * gb1                      (period-1 values; checkpoints 1 and 2)
  bond side pays the fixed advisory charge c:  Bc = B1 - c,  W = E1 + Bc
  purchase P with fee f*P, both from the bond side, solved so that
      E1 + P = w * (W - f*P)   =>   P = (w*W - E1) / (1 + w*f)
  E2 = E1 + P, B2 = Bc - P - f*P
  managed terminal  = E2 * ge2 + B2 * gb2
  benchmark terminal = w * ge1 * ge2 + (1 - w) * gb1 * gb2
  final = (managed - benchmark) * 100   (percent of original notional, unrounded)

The purchase equation is applied exactly as stated (signed closed form); no clamp is imposed.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h013"


def solve(text: str, q: dict) -> dict:
    w = grab(r"starts with equity weight {N}", text)
    ge1, gb1 = grab_all(r"During period 1, equity and bonds grow by factors {N} and {N}", text)
    charge = grab(r"advisory charge equal to {N} of original initial notional", text)
    fee = grab(r"transaction fee rate {N}", text)
    ge2, gb2 = grab_all(r"During period 2, equity and bonds grow by factors {N} and {N}", text)

    one = Fraction(1)
    # Period-1 values per unit of original notional (before any midpoint charge).
    e1 = w * ge1
    b1 = (one - w) * gb1

    # Midpoint: fixed advisory charge from the bond side.
    b_charged = b1 - charge
    wealth_after_charge = e1 + b_charged

    # Purchase so equity = target fraction (starting weight) of wealth after both charges.
    purchase = (w * wealth_after_charge - e1) / (one + w * fee)
    e_mid = e1 + purchase
    b_mid = b_charged - purchase - fee * purchase
    assert e_mid == w * (e_mid + b_mid)

    managed = e_mid * ge2 + b_mid * gb2
    benchmark = w * ge1 * ge2 + (one - w) * gb1 * gb2
    final = (managed - benchmark) * 100

    return {
        "final": final,
        "slots": {
            "period_1_equity_value_checkpoint": e1,
            "period_1_bond_value_checkpoint": b1,
        },
    }
