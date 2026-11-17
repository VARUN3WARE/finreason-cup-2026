from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h092"


def solve(text: str, q: dict) -> dict:
    ni = grab(r"after-tax net income {N}", text)
    dep = grab(r"depreciation {N}", text)
    amo = grab(r"amortization {N}", text)
    ar = grab(r"increase in accounts receivable {N}", text)
    inv = grab(r"increase in inventory {N}", text)
    ap = grab(r"decrease in accounts payable {N}", text)
    accr = grab(r"accrued liabilities excluding income taxes payable {N}", text)
    itp = grab(r"increase in income taxes payable {N}", text)
    pay = grab(r"non-tax operating cash payments {N}", text)
    tax = grab(r"cash income taxes paid {N}", text)
    rec = grab(r"operating cash receipts {N}", text)
    rev = grab(r"reported revenue {N}", text)

    noncash = dep + amo
    wc_uses = ar + inv + ap
    direct_uses = pay + tax

    ocf_ind = ni + noncash - wc_uses + accr + itp
    ocf_dir = rec - direct_uses

    m_ind = ocf_ind / rev
    m_dir = ocf_dir / rev
    score = (m_ind + m_dir) / 2 - (m_ind - m_dir) ** 2

    return {
        "final": Fraction(score) * 100,
        "slots": {
            "noncash_charges_checkpoint": noncash,
            "working_capital_cash_uses_checkpoint": wc_uses,
            "direct_cash_uses_checkpoint": direct_uses,
        },
    }
