"""h111 -- two-method enterprise valuation with a dispersion-tolerance reconciliation, then EV -> equity.

Structure (identical wording in all 3 instances, numbers differ):
  "The revenue method uses revenue R and revenue multiple mR. The EBITDA method uses EBITDA E and
   EBITDA multiple mE. Compare the two enterprise values: their dispersion is the higher value minus
   the lower value, and the permitted dispersion equals the lower value multiplied by t. If the methods
   are consistent within that tolerance, use their mean enterprise value; otherwise use the lower
   enterprise value. Then deduct total debt D and add cash C ... Report the reconciled equity value."

AMBIGUITIES HUNTED AND RESOLVED (with textual evidence):
  A1. Units. The text carries no unit words; answer_spec and both slot specs are unit "usd_million", and
      every input (revenue, EBITDA, debt, cash) is given as a bare number in the same scale. => all
      inputs are already USD millions; no scaling anywhere.
  A2. "revenue multiple 3" / "EBITDA multiple 9" are plain EV multiples (ratios), never percents.
      EV_rev = revenue * revenue multiple; EV_ebitda = EBITDA * EBITDA multiple.
  A3. "the permitted dispersion equals the lower value multiplied by 0.2": 0.2 is a plain ratio (no
      "percent" in the text). Defensive guard only: if the word percent/% immediately follows that factor
      in some instance, divide by 100. "the lower value" refers to the lower of the two ENTERPRISE VALUES
      (the sentence opens with "Compare the two enterprise values: ..."), not to a multiple or revenue.
  A4. "their dispersion is the higher value minus the lower value" => dispersion = max(EV) - min(EV) >= 0.
  A5. "consistent within that tolerance": "within" is inclusive, so consistent iff dispersion <= permitted
      dispersion. (In all 3 shown instances dispersion exceeds the tolerance by a wide margin, so the
      tie convention does not alter any outcome; implemented as <= to honour the wording.)
  A6. "use their mean enterprise value" = simple arithmetic mean (EV_rev + EV_ebitda) / 2;
      "otherwise use the lower enterprise value" = min(EV_rev, EV_ebitda).
  A7. "Then deduct total debt D and add cash C, which are the only enterprise-value-to-equity-value
      adjustments" => equity = chosen EV - D + C. No floor at zero, no other adjustments, sign preserved.
  A8. Rounding: no sentence says any intermediate quantity is rounded before reuse, so every value is
      returned as an exact Fraction; the framework rounds the final and each checkpoint half-up to 2 dp
      independently. (Instance 3 yields exactly 105.865 -> 105.87; exact arithmetic is essential there.)
  A9. Checkpoints: revenue_value_checkpoint = EV under the revenue method (A2, unrounded, USD m);
      ebitda_value_checkpoint = EV under the EBITDA method (A2, unrounded, USD m). They are the two
      method values BEFORE any reconciliation or equity adjustment.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, after, grab

TEMPLATE_ID = "h111"


def _grab_or_after(pattern: str, text: str, phrase: str) -> Fraction:
    """Anchored regex first; fall back to the first number after a shorter phrase."""
    try:
        return grab(pattern, text)
    except ValueError:
        return after(text, phrase)


def _tolerance_factor(text: str) -> Fraction:
    """Factor t in 'the lower value multiplied by t' (ratio; percent guard, see A3)."""
    m = re.search(
        r"lower\s+(?:enterprise\s+)?value\s+multiplied\s+by\s+(" + NUMBER + r")\s*(percent|%)?",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        return after(text, "multiplied by")
    t = F(m.group(1))
    if m.group(2):
        t = t / 100
    return t


def solve(text: str, q: dict) -> dict:
    # --- inputs (A1, A2): bare numbers already in USD millions; multiples are plain ratios.
    revenue = _grab_or_after(r"uses\s+revenue\s+{N}\s+and\s+revenue\s+multiple", text, "uses revenue")
    rev_multiple = _grab_or_after(r"revenue\s+multiple\s+{N}", text, "revenue multiple")
    ebitda = _grab_or_after(r"uses\s+EBITDA\s+{N}\s+and\s+EBITDA\s+multiple", text, "uses EBITDA")
    ebitda_multiple = _grab_or_after(r"EBITDA\s+multiple\s+{N}", text, "EBITDA multiple")
    tol_factor = _tolerance_factor(text)  # A3
    debt = _grab_or_after(r"deduct\s+total\s+debt\s+{N}", text, "total debt")
    cash = _grab_or_after(r"add\s+cash\s+{N}", text, "cash")

    # --- the two method enterprise values (A2, A9)
    ev_revenue = revenue * rev_multiple
    ev_ebitda = ebitda * ebitda_multiple

    # --- reconciliation policy (A4, A5, A6)
    higher = max(ev_revenue, ev_ebitda)
    lower = min(ev_revenue, ev_ebitda)
    dispersion = higher - lower
    permitted = lower * tol_factor
    if dispersion <= permitted:  # "consistent within that tolerance" (inclusive)
        ev = (ev_revenue + ev_ebitda) / 2  # mean enterprise value
    else:
        ev = lower  # lower enterprise value

    # --- EV -> equity (A7): deduct total debt, add cash; nothing else, no floor.
    equity = ev - debt + cash

    return {
        "final": equity,
        "slots": {
            "revenue_value_checkpoint": ev_revenue,
            "ebitda_value_checkpoint": ev_ebitda,
        },
    }
