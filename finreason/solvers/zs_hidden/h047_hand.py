"""h047: standard vs itemized tax method choice with eligibility flag.

taxable_m   = max(0, gross - deduction_m)
liability_m = max(0, rate * taxable_m - credit_m)
Use itemized only when eligible AND liability_itemized < liability_standard (strict).
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h047"


def _rate(text: str) -> Fraction:
    m = re.search(r"tax rate is (" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("tax rate not found")
    r = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        r /= 100
    return r


def _eligible(text: str) -> bool:
    m = re.search(r"may be used only when\s+(\w+)\s+is\s+(\w+)", text)
    if m is None:
        raise ValueError("eligibility clause not found")
    a, b = m.group(1).lower(), m.group(2).lower()
    if a not in ("true", "false") or b not in ("true", "false"):
        raise ValueError(f"unexpected eligibility tokens {a!r} {b!r}")
    return a == b


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross income is (?:USD )?\$?{N}", text)
    rate = _rate(text)
    d_std = grab(r"standard method permits a deduction of (?:USD )?\$?{N}", text)
    c_std = grab(r"standard method permits a deduction of .*? and a credit of (?:USD )?\$?{N}", text)
    d_itm = grab(r"itemized method permits a deduction of (?:USD )?\$?{N}", text)
    c_itm = grab(r"itemized method permits a deduction of .*? and a credit of (?:USD )?\$?{N}", text)
    eligible = _eligible(text)

    zero = Fraction(0)
    tax_std = max(zero, gross - d_std)
    tax_itm = max(zero, gross - d_itm)
    liab_std = max(zero, rate * tax_std - c_std)
    liab_itm = max(zero, rate * tax_itm - c_itm)

    final = liab_itm if (eligible and liab_itm < liab_std) else liab_std

    return {
        "final": final,
        "slots": {
            "standard_taxable_checkpoint": tax_std,
            "itemized_taxable_checkpoint": tax_itm,
        },
    }
