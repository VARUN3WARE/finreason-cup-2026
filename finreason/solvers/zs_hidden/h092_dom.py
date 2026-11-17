"""h092 -- fictional operating-cash-flow reconciliation score.

FINANCE MODEL (written before coding)
-------------------------------------
Two operating-cash-flow (OCF) schedules for the same period:

  Indirect method (standard convention):
      OCF_ind = NI
                + depreciation + amortization            (noncash charges; text says "nonoverlapping",
                                                           so they are simply additive, no double count)
                - increase in accounts receivable        (cash use)
                - increase in inventory                  (cash use)
                - decrease in accounts payable           (cash use: paying suppliers down)
                + increase in accrued liabilities ex-taxes payable   (cash source)
                + increase in income taxes payable                    (cash source)
      The three "cash uses" are all given as positive magnitudes and are SUBTRACTED
      (the text says "subtracts the cash uses from ..."); the two accrual increases are ADDED.

  Direct method:
      OCF_dir = operating cash receipts - non-tax operating cash payments - cash income taxes paid.

  Margins (normalisation by reported revenue R):
      m_ind = OCF_ind / R,   m_dir = OCF_dir / R      (plain ratios)

  Fictional reconciliation score (scenario-local, text-defined):
      score = (m_ind + m_dir)/2 - (m_ind - m_dir)^2
      where the squared term is the square of the signed difference of the two margins as
      plain ratios (the difference sign is irrelevant after squaring).
      Reported as a percentage: score * 100  (unit "percent": 12.5 means 12.5%).

CHECKPOINTS
  noncash_charges_checkpoint            = depreciation + amortization              (USD million)
  working_capital_cash_uses_checkpoint  = AR increase + inventory increase + AP decrease  (USD million)
  direct_cash_uses_checkpoint           = non-tax operating payments + cash income taxes paid (USD million)

Overrides / interpretation notes:
  - The square is taken on the ratio-scale difference (not on percentage points); the final
    result is only then multiplied by 100.
  - No intermediate rounding anywhere; framework rounds the final and each slot half-up to 2 dp.
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h092"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"after-tax net income {N}", text)
    dep = grab(r"nonoverlapping depreciation {N}", text)
    amort = grab(r"and amortization {N}", text)
    d_ar = grab(r"increase in accounts receivable {N}", text)
    d_inv = grab(r"increase in inventory {N}", text)
    d_ap = grab(r"decrease in accounts payable {N}", text)
    d_accr = grab(r"increase in accrued liabilities excluding income taxes payable {N}", text)
    d_taxp = grab(r"increase in income taxes payable {N}", text)

    nontax_pay = grab(r"non-tax operating cash payments {N}", text)
    tax_paid = grab(r"cash income taxes paid {N}", text)
    receipts = grab(r"operating cash receipts {N}", text)
    revenue = grab(r"reported revenue {N}", text)

    noncash = dep + amort
    wc_uses = d_ar + d_inv + d_ap
    direct_uses = nontax_pay + tax_paid

    ocf_ind = ni + noncash - wc_uses + d_accr + d_taxp
    ocf_dir = receipts - direct_uses

    m_ind = ocf_ind / revenue
    m_dir = ocf_dir / revenue
    diff = m_ind - m_dir
    score = (m_ind + m_dir) / 2 - diff * diff
    final = score * 100

    return {
        "final": final,
        "slots": {
            "noncash_charges_checkpoint": noncash,
            "working_capital_cash_uses_checkpoint": wc_uses,
            "direct_cash_uses_checkpoint": direct_uses,
        },
    }
