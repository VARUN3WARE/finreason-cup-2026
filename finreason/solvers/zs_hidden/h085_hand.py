"""h085: current loan vs refinance (fee capitalized), two-period balance roll-forward.

Each period: interest accrues first (balance * (1 + r)), then the period-end payment is subtracted.
Refinance opening balance = principal + capitalized fee.
Final = current-loan balance after period 2 minus refinance balance after period 2 (signed).
"""
from fractions import Fraction
import re

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h085"

_ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6}


def _rate(seg: str) -> Fraction:
    m = re.search(rf"effective rate of ({NUMBER})\s*(percent|%)?", seg)
    if m is None:
        raise ValueError("rate not found")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def _roll(bal: Fraction, r: Fraction, pmt: Fraction, n: int) -> list:
    out = []
    for _ in range(n):
        bal = bal * (1 + r) - pmt
        out.append(bal)
    return out


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"outstanding principal of (?:USD )?\$?{N}", text)

    i_cur = text.index("The current loan uses")
    i_ref = text.index("The refinance capitalizes")
    cur_seg = text[i_cur:i_ref]
    ref_seg = text[i_ref:]
    cut = ref_seg.find("Interest accrues")
    if cut > 0:
        ref_seg = ref_seg[:cut]

    r_cur = _rate(cur_seg)
    pmt_cur = grab(r"payment of (?:USD )?\$?{N}", cur_seg)
    fee = grab(r"fee of (?:USD )?\$?{N}", ref_seg)
    r_ref = _rate(ref_seg)
    pmt_ref = grab(r"payment of (?:USD )?\$?{N}", ref_seg)

    m = re.search(r"(\w+)-period ending-balance difference", text)
    n = _ORD.get(m.group(1).lower(), 2) if m else 2

    cur = _roll(p0, r_cur, pmt_cur, n)
    ref = _roll(p0 + fee, r_ref, pmt_ref, n)

    return {
        "final": cur[n - 1] - ref[n - 1],
        "slots": {
            "current_first_payment_balance_checkpoint": cur[0],
            "refinance_first_payment_balance_checkpoint": ref[0],
        },
    }
