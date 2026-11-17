"""h092 -- indirect vs direct operating cash flow, fictional "reconciliation score".

AMBIGUITIES CONSIDERED AND RESOLVED (textual evidence in brackets):

1. Ratio vs percent inside the score.  The margins are defined by "Normalize each
   schedule's operating cash flow by reported revenue" -> dimensionless ratios.
   The score is "the mean of those two margins minus the square of their signed
   difference" computed on those ratios; only afterwards "Report the score as a
   percentage".  So score = (m1+m2)/2 - (m1-m2)^2 on RATIOS, then x100.
   (Squaring percent-form margins would give e.g. -47 for instance 1 -- absurd and
   dimensionally inconsistent; "report ... as a percentage" is a presentation step.)

2. Order of the signed difference: irrelevant because it is squared.

3. Indirect OCF composition [sentence 2]:
       NI + depreciation + amortization
       - (AR increase + inventory increase + AP decrease)        # "subtracts the cash uses"
       + accrued-liabilities increase + income-taxes-payable increase   # "then adds"
   "nonoverlapping" depreciation and amortization => both are added in full, no
   double-count adjustment.

4. Direction words.  All three instances say increase/increase/decrease for
   AR/inventory/AP and increase/increase for accrued liabilities / taxes payable.
   The parser still reads the direction word, so a flipped sign in a sibling
   instance would be handled with standard indirect-method signs
   (asset increase = use, liability decrease = use, and vice versa).

5. Checkpoint 1 "total noncash depreciation and amortization charges" =
   depreciation + amortization, USD millions (positive).

6. Checkpoint 2 "cash uses from the three working-capital movements" = the three
   items the text labels "the cash uses" (AR, inventory, AP), summed as a POSITIVE
   use amount (the text "subtracts the cash uses", so the uses themselves are
   positive).  The accrued-liabilities and taxes-payable items are NOT among "the
   three" -- they are introduced separately with "then adds".

7. Checkpoint 3 "non-tax operating cash payments plus cash income taxes paid" =
   plain sum of the two direct-schedule deductions, positive, USD millions.

8. Revenue: "reported revenue N" is the single normalizer for both schedules.

9. Rounding: nothing is rounded inside the chain ("use exact arithmetic and round
   only the final percentage"); all returned values are exact Fractions and the
   framework applies half-up 2dp.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h092"


def _directed(label: str, text: str) -> tuple[str, Fraction]:
    """Return (direction, amount) for 'an increase/decrease in <label> N'."""
    m = re.search(r"(increase|decrease) in " + label + r" (" + NUMBER + r")", text, flags=re.S)
    if m is None:
        raise ValueError(f"no directed movement for {label!r}")
    return m.group(1), F(m.group(2))


def _asset_use(label: str, text: str) -> Fraction:
    """Cash use from an operating asset movement: increase = use (+), decrease = source (-)."""
    d, amt = _directed(label, text)
    return amt if d == "increase" else -amt


def _liability_add(label: str, text: str) -> Fraction:
    """Add-back from an operating liability movement: increase = add (+), decrease = subtract (-)."""
    d, amt = _directed(label, text)
    return amt if d == "increase" else -amt


def solve(text: str, q: dict) -> dict:
    # --- indirect schedule inputs
    net_income = grab(r"after-tax net income {N}", text)
    depreciation = grab(r"depreciation {N}", text)
    amortization = grab(r"amortization {N}", text)

    ar_use = _asset_use(r"accounts receivable", text)
    inv_use = _asset_use(r"inventory", text)
    # Accounts payable is a liability: a DECREASE is a cash use.
    ap_dir, ap_amt = _directed(r"accounts payable", text)
    ap_use = ap_amt if ap_dir == "decrease" else -ap_amt

    accrued_add = _liability_add(r"accrued liabilities excluding income taxes payable", text)
    taxes_payable_add = _liability_add(r"income taxes payable", text)

    # --- direct schedule inputs
    receipts = grab(r"operating cash receipts {N}", text)
    non_tax_payments = grab(r"non-tax operating cash payments {N}", text)
    cash_taxes = grab(r"cash income taxes paid {N}", text)

    revenue = grab(r"reported revenue {N}", text)

    # --- checkpoints
    noncash_charges = depreciation + amortization
    wc_cash_uses = ar_use + inv_use + ap_use
    direct_cash_uses = non_tax_payments + cash_taxes

    # --- operating cash flows
    ocf_indirect = net_income + noncash_charges - wc_cash_uses + accrued_add + taxes_payable_add
    ocf_direct = receipts - direct_cash_uses

    # --- margins (ratios) and fictional reconciliation score
    m_ind = ocf_indirect / revenue
    m_dir = ocf_direct / revenue
    score = (m_ind + m_dir) / 2 - (m_ind - m_dir) ** 2

    return {
        "final": score * 100,  # reported as a percentage
        "slots": {
            "noncash_charges_checkpoint": noncash_charges,
            "working_capital_cash_uses_checkpoint": wc_cash_uses,
            "direct_cash_uses_checkpoint": direct_cash_uses,
        },
    }
