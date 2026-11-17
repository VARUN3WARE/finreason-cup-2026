"""h111: two-method (revenue multiple vs EBITDA multiple) valuation with a
dispersion-tolerance reconciliation policy, then EV -> equity bridge.

Chain:
  EV_rev    = revenue * revenue multiple                  (slot 1)
  EV_ebitda = EBITDA * EBITDA multiple                    (slot 2)
  dispersion = higher EV - lower EV
  permitted  = lower EV * tolerance factor
  consistent (dispersion within permitted, i.e. <=)  -> mean of the two EVs
  otherwise                                          -> lower EV
  equity = reconciled EV - total debt + cash              (final)
"""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h111"


def _tolerance(text: str) -> Fraction:
    """Factor applied to the lower EV (stated as a plain multiplier, e.g. 0.2)."""
    m = re.search(rf"lower (?:enterprise )?value multiplied by ({NUMBER})(\s*(?:percent|%))?", text)
    if m is None:
        raise ValueError("tolerance factor not found")
    factor = F(m.group(1))
    return factor / 100 if m.group(2) else factor


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"revenue method uses revenue {N}", text)
    rev_mult = grab(r"revenue multiple {N}", text)
    ebitda = grab(r"EBITDA method uses EBITDA {N}", text)
    ebitda_mult = grab(r"EBITDA multiple {N}", text)
    tol = _tolerance(text)
    debt = grab(r"deduct total debt {N}", text)
    cash = grab(r"add cash {N}", text)

    ev_rev = revenue * rev_mult
    ev_ebitda = ebitda * ebitda_mult

    hi = max(ev_rev, ev_ebitda)
    lo = min(ev_rev, ev_ebitda)
    dispersion = hi - lo
    permitted = lo * tol

    if dispersion <= permitted:  # "consistent within that tolerance"
        ev = (ev_rev + ev_ebitda) / 2
    else:
        ev = lo

    equity = ev - debt + cash

    return {
        "final": equity,
        "slots": {
            "revenue_value_checkpoint": ev_rev,
            "ebitda_value_checkpoint": ev_ebitda,
        },
    }
