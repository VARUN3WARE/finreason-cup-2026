"""h013 -- managed two-period portfolio (midpoint advisory charge + fee-bearing equity
purchase back to target weight) versus a fee-free buy-and-hold benchmark.

AMBIGUITY HUNT -- points where two analysts could disagree, and the resolution used:

A1. What are the two checkpoints?  "period-1 equity value" / "period-1 bond value" per unit
    of original notional.  Resolution: the values right after period-1 growth and BEFORE any
    midpoint event: E1 = w * g_e1, B1 = (1 - w) * g_b1.  Evidence: the advisory charge and the
    purchase happen "At the midpoint", not "During period 1"; the slots sit at positions 1 and
    2, i.e. the first two links of the chain, before the midpoint step.  (Alternative rejected:
    bond value after the advisory charge -- that is a midpoint quantity, not a period-1 one.)

A2. Which "target fraction"?  Resolution: the original equity weight w ("starts with equity
    weight w" ... "its equity target" / "its target fraction of wealth").  No other target is
    stated.

A3. Wealth base for the target: "equity equals its target fraction of wealth after BOTH
    midpoint charges".  Resolution: W = E1 + B1 - c - f*x (advisory charge AND the transaction
    fee on the purchase both reduce wealth), so
        E1 + x = w * (E1 + B1 - c - f*x)   =>   x = (w*(E1 + B1 - c) - E1) / (1 + w*f).
    (Alternative rejected: solving against wealth after only the advisory charge would leave
    equity != target once the fee is paid, contradicting "after both midpoint charges".)

A4. Fee base: "transaction fee rate f on the purchase" -> fee = f * x on the purchase amount
    (not on wealth, not grossed-up).  Both the purchase price x and the fee f*x leave the bond
    side ("also from the bond side"), so B2 = B1 - c - x - f*x and E2 = E1 + x.

A5. Advisory charge base: "equal to c of ORIGINAL initial notional" -> a fixed amount c per
    unit of notional (not c of current wealth / bond value), taken "entirely from the bond side".

A6. Branch: the text asserts "The portfolio is then below its equity target. The advisor buys
    equity ...".  In the instance with period-1 equity factor 2 the portfolio is in fact ABOVE
    target, so the literal "solve the purchase" equation gives x < 0 (a sale) with the algebraic
    fee f*x < 0.  The text contains no conditional, no sell branch, no floor at zero and no
    absolute-value fee rule, so the resolution is: apply the stated equation unconditionally
    (sign preserved).  Alternatives considered and rejected as unworded: (i) clamp x at 0 /
    skip the trade; (ii) treat as a sale with fee on |x| paid from bonds (x = (E1 - w*(E1+B1-c))
    /(1 - w*f) sold).  This is the single largest risk in the cluster.

A7. Benchmark: "retains the original equity and bond positions through both periods ... pays
    neither midpoint charge" -> w*g_e1*g_e2 + (1-w)*g_b1*g_b2, no rebalance, no charges.

A8. Final quantity: "managed wealth minus benchmark wealth as a percentage of original initial
    notional", "positive result favors the managed path" -> (managed - benchmark) * 100, with
    sign kept (may be negative).  Unit percent, so 100x the per-unit difference.

A9. "Growth factors are wealth multipliers, not return rates" -> multiply directly, no 1+.

A10. "complementary bond weight" -> 1 - w.  All arithmetic exact (Fraction); no rounding
     anywhere inside the chain (the text rounds only the final percentage).
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h013"


def solve(text: str, q: dict) -> dict:
    # --- parameters -----------------------------------------------------------------------
    w = grab(r"starts with equity weight {N}", text)
    g_e1, g_b1 = grab_all(r"During period 1, equity and bonds grow by factors {N} and {N}", text)
    c = grab(r"advisory charge equal to {N} of original initial notional", text)
    f = grab(r"transaction fee rate {N} on the purchase", text)
    g_e2, g_b2 = grab_all(r"During period 2, equity and bonds grow by factors {N} and {N}", text)

    w_b = Fraction(1) - w  # complementary bond weight (A10)

    # --- period 1 growth (checkpoints, A1) ------------------------------------------------
    e1 = w * g_e1
    b1 = w_b * g_b1

    # --- midpoint: fixed advisory charge from bonds (A5) ----------------------------------
    b1_after_charge = b1 - c

    # --- midpoint: purchase x so that E1 + x = w * (E1 + B1 - c - f*x)  (A3, A4, A6) -------
    x = (w * (e1 + b1_after_charge) - e1) / (Fraction(1) + w * f)
    fee = f * x
    e2 = e1 + x
    b2 = b1_after_charge - x - fee

    # --- period 2 growth ------------------------------------------------------------------
    managed = e2 * g_e2 + b2 * g_b2

    # --- fee-free buy-and-hold benchmark (A7) ---------------------------------------------
    benchmark = w * g_e1 * g_e2 + w_b * g_b1 * g_b2

    # --- managed minus benchmark, in percent of original notional (A8) --------------------
    final = (managed - benchmark) * 100

    return {
        "final": final,
        "slots": {
            "period_1_equity_value_checkpoint": e1,
            "period_1_bond_value_checkpoint": b1,
        },
    }
