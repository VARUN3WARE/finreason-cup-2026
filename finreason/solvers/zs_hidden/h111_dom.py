"""h111 -- two-method relative valuation, reconciled under a consistency policy, then EV -> equity.

FINANCE MODEL (written before the code)
=======================================
Quantity: the buyer's RECONCILED EQUITY VALUE of a target, in USD millions, from a market-multiple
(relative) valuation done two ways.  Every figure in the text is already in USD millions, so the
result needs no unit scaling.

1) Method values (both are ENTERPRISE values -- value of operations, before capital structure):
       EV_rev    = revenue x revenue multiple          (EV / Revenue method)
       EV_ebitda = EBITDA  x EBITDA  multiple          (EV / EBITDA  method)
   These two numbers are the two checkpoints (position 1 = revenue method, position 2 = EBITDA
   method).  They are reported UNROUNDED; the framework rounds each to 2 dp half-up.

2) Reconciliation policy (the buyer's stated policy; it overrides the usual "just average" habit):
       hi, lo       = max / min of {EV_rev, EV_ebitda}
       dispersion   = hi - lo
       permitted    = lo x tolerance        (tolerance is given as a plain fraction, 0.2 or 0.15, so it
                                            is NOT divided by 100 -- "multiplied by 0.2" is literal)
       consistent   = dispersion <= permitted   ("consistent WITHIN that tolerance" -> boundary included;
                                                 none of the 3 instances sits on the boundary)
       EV_reconciled = (EV_rev + EV_ebitda) / 2   if consistent     ("their mean enterprise value")
                       lo                          otherwise         ("the lower enterprise value")
   Note the tolerance base is the LOWER value (not the higher, not the mean).

3) EV -> equity bridge.  The text says total debt and cash are the ONLY adjustments in this scenario,
   so (override of the generic bridge: no minority interest, preferred equity, leases, pensions, etc.):
       Equity = EV_reconciled - total debt + cash
   Debt is deducted, cash is added (cash 4.865 is a decimal with a 3-dp tail, so the final can be an
   exact half-up tie at the 3rd decimal -- exact Fraction arithmetic and round_half_up handle that).

4) Final answer = reconciled equity value (usd_million, 2 dp half-up).  No intermediate rounding is
   used anywhere in the chain: nothing in the text says a rounded value feeds downstream.

Override notes: (a) policy picks LOWER EV, not mean, when inconsistent; (b) tolerance is a fraction,
not a percent; (c) only debt and cash bridge EV to equity.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h111"


def solve(text: str, q: dict) -> dict:
    # ---- inputs, anchored on the surrounding words -------------------------------------------
    revenue, rev_mult = grab_all(r"revenue method uses revenue {N} and revenue multiple {N}", text)
    ebitda, ebitda_mult = grab_all(r"EBITDA method uses EBITDA {N} and EBITDA multiple {N}", text)
    tolerance = grab(r"permitted dispersion equals the lower value multiplied by {N}", text)
    debt = grab(r"deduct total debt {N}", text)
    cash = grab(r"add cash {N}", text)

    # ---- 1) the two method enterprise values --------------------------------------------------
    ev_rev = revenue * rev_mult
    ev_ebitda = ebitda * ebitda_mult

    # ---- 2) reconciliation policy -------------------------------------------------------------
    lo = min(ev_rev, ev_ebitda)
    hi = max(ev_rev, ev_ebitda)
    dispersion = hi - lo
    permitted = lo * tolerance
    consistent = dispersion <= permitted  # "within that tolerance": inclusive of the boundary
    if consistent:
        ev_reconciled = (ev_rev + ev_ebitda) / 2
    else:
        ev_reconciled = lo

    # ---- 3) EV -> equity ----------------------------------------------------------------------
    equity = ev_reconciled - debt + cash

    return {
        "final": Fraction(equity),
        "slots": {
            "revenue_value_checkpoint": Fraction(ev_rev),
            "ebitda_value_checkpoint": Fraction(ev_ebitda),
        },
    }
