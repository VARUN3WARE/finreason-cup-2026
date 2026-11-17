"""h095 -- normalized operating cash flow / adjusted EBITDA screen: max supportable
noncash add-back and signed headroom versus the proposed add-back.

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED (textual evidence):

1. What the checkpoint denotes.  Slot "cash_flow_after_working_capital_checkpoint"
   (position 1) is described as "Remove the temporary working-capital release from
   reported operating cash flow".  Only the working-capital release is named, so the
   checkpoint is  OCF_reported - WC_release  (the tax refund is removed in the NEXT
   step, not here).  Unit usd_million, unrounded (framework rounds to 4 dp).

2. Which items the reviewer removes.  "... including a temporary working-capital
   release of W and a one-time tax refund of T that the reviewer removes."  Both are
   non-recurring cash INFLOWS that are "included" in reported OCF; the checkpoint
   confirms the release is removed and the relative clause removes the refund.  So
   normalized OCF = OCF - W - T  (subtract both; a "release" is a source of cash).

3. Denominator of the screen.  "normalized operating cash flow divided by EBITDA
   after the proposed noncash management add-back of A" -> denominator is
   E_verified + X where X is the add-back under test.  "Assume the proposed add-back
   has no operating-cash-flow effect" -> numerator is NOT changed by X.

4. Strict vs non-strict.  "to be at least r" is >=, so the screen is satisfied on the
   boundary and the maximum add-back is attained:  X_max = normOCF / r - E.
   (With a strict ">" there would be no maximum; "at least" rules that out.)

5. Threshold units.  "at least 0.6" is a plain ratio (OCF/EBITDA), not a percent.
   Defensive parsing: if the threshold is immediately followed by "percent" or "%"
   it is divided by 100.

6. Headroom sign convention.  "report the signed headroom relative to the proposed
   add-back. A positive result means unused screening capacity" -> headroom =
   X_max - A_proposed.  No floor at zero is stated, so none is applied (for all three
   instances X_max > 0 anyway, so a floor would not change anything).

7. Units.  Every amount is in USD millions already; the answer unit is usd_million,
   so no scaling.  All arithmetic exact (Fraction); instance 2's final value is
   exactly 5.445, a half-up tie that only exact arithmetic resolves correctly to 5.45.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab, F

TEMPLATE_ID = "h095"


def _threshold(text: str) -> Fraction:
    """Screen threshold as a plain ratio; tolerate a percent-style phrasing."""
    m = re.search(
        r"(?:at\s+least|no\s+less\s+than|not\s+(?:be\s+)?(?:less|lower)\s+than|minimum\s+of)\s+(" + NUMBER + r")(\s*(?:percent|%))?",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        raise ValueError("screen threshold not found")
    r = F(m.group(1))
    if m.group(2):
        r = r / 100
    return r


def solve(text: str, q: dict) -> dict:
    # Verified recurring EBITDA before the proposed adjustment.
    ebitda = grab(r"EBITDA\s+before\s+the\s+proposed\s+adjustment\s+(?:is|of|was|equals)\s+{N}", text)

    # Reported operating cash flow (includes the two items to be removed).
    ocf = grab(r"[Rr]eported\s+operating\s+cash\s+flow\s+(?:is|of|was|equals)\s+{N}", text)

    # Temporary working-capital release (cash inflow included in reported OCF).
    wc_release = grab(r"working[\s-]*capital\s+release\s+of\s+{N}", text)

    # One-time tax refund (cash inflow included in reported OCF).
    tax_refund = grab(r"tax\s+refund\s+of\s+{N}", text)

    # Proposed noncash management add-back.
    proposed = grab(r"add[\s-]*back\s+of\s+{N}", text)

    # Screen threshold (ratio).
    ratio = _threshold(text)

    # Step 1 (checkpoint): remove the working-capital release only.
    cf_after_wc = ocf - wc_release

    # Step 2: remove the one-time tax refund -> normalized operating cash flow.
    normalized_ocf = cf_after_wc - tax_refund

    # Step 3: maximum add-back X with normalized_ocf / (ebitda + X) >= ratio.
    #         X_max = normalized_ocf / ratio - ebitda  (boundary attained: "at least").
    max_addback = normalized_ocf / ratio - ebitda

    # Step 4: signed headroom relative to the proposed add-back.
    headroom = max_addback - proposed

    return {
        "final": headroom,
        "slots": {"cash_flow_after_working_capital_checkpoint": cf_after_wc},
    }
