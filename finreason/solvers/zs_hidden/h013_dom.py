"""h013 -- managed (rebalanced, fee-bearing) two-period portfolio vs fee-free buy-and-hold.

FINANCE MODEL (all wealth per 1 USD of ORIGINAL initial notional)
-----------------------------------------------------------------
Inputs: w   = initial equity weight (also the equity TARGET fraction used at the rebalance)
        1-w = complementary bond weight
        gE1, gB1 = period-1 wealth multipliers for equity / bonds   (multipliers, NOT returns)
        c   = fixed advisory charge (fraction of ORIGINAL notional, i.e. USD since notional = 1),
              deducted entirely from the bond side at the midpoint
        f   = proportional transaction-fee rate on the equity purchase, paid from the bond side
        gE2, gB2 = period-2 wealth multipliers

1. Start:            E0 = w,  B0 = 1 - w.
2. Period-1 growth:  E1 = E0*gE1,  B1 = B0*gB1.            <- the two checkpoints
                     (period-1 equity / bond value, after period-1 growth, before any midpoint action)
3. Midpoint advisory charge (bond side only): B1' = B1 - c.  Wealth W' = E1 + B1'.
4. Rebalance: buy P of equity paying fee f*P, all out of the bond side:
        equity  = E1 + P
        bond    = B1' - P - f*P
        wealth after both midpoint charges = E1 + B1' - f*P
   Require equity = w * (wealth after both charges):
        E1 + P = w*(E1 + B1' - f*P)   =>   P = (w*(E1 + B1') - E1) / (1 + w*f)
   P > 0 is a purchase (the case narrated in the text).  The text's rule is applied literally
   as a signed linear equation; if P happened to be negative (equity above target although the
   text narrates "below"), the same signed equation is used (no extra sale rule is stated).
5. Period-2 growth:  managed terminal M = (E1+P)*gE2 + (B1'-P-f*P)*gB2.
6. Benchmark (fee-free buy-and-hold, original positions, no rebalance, no charges):
        BH = E0*gE1*gE2 + B0*gB1*gB2.
7. Answer = (M - BH) / (original notional = 1) * 100   [percent]; positive favours managed.

Overrides of standard convention: none (target fraction = initial equity weight; fee base = purchase
amount; the fee is an extra cost on top of the purchase, both paid from the bond side).
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h013"


def solve(text: str, q: dict) -> dict:
    w = grab(r"starts with equity weight {N}", text)
    gE1, gB1 = grab_all(r"During period 1, equity and bonds grow by factors {N} and {N}", text)
    c = grab(r"advisory charge equal to {N} of original initial notional", text)
    f = grab(r"transaction fee rate {N} on the purchase", text)
    gE2, gB2 = grab_all(r"During period 2, equity and bonds grow by factors {N} and {N}", text)

    E0 = w
    B0 = 1 - w

    # period-1 growth (checkpoints)
    E1 = E0 * gE1
    B1 = B0 * gB1

    # midpoint advisory charge, bond side only
    B1c = B1 - c

    # equity purchase solving E1 + P = w * (E1 + B1c - f*P)
    P = (w * (E1 + B1c) - E1) / (1 + w * f)
    E_m = E1 + P
    B_m = B1c - P - f * P

    managed = E_m * gE2 + B_m * gB2
    bench = E0 * gE1 * gE2 + B0 * gB1 * gB2

    final = (managed - bench) * 100

    return {
        "final": final,
        "slots": {
            "period_1_equity_value_checkpoint": E1,
            "period_1_bond_value_checkpoint": B1,
        },
    }
