"""h047 -- simplified two-method tax liability (standard vs itemized).

FINANCE MODEL
-------------
Inputs: gross income G, flat tax rate t (as a decimal fraction, 0.3 = 30%).
Each method m in {standard, itemized} has a deduction D_m and a credit C_m.

  taxable_m = max(0, G - D_m)               (deduction reduces income; taxable income
                                              cannot be negative -- standard convention)
  tax_m     = t * taxable_m                  (flat rate on taxable income)
  net_m     = max(0, tax_m - C_m)            (credit is a dollar-for-dollar reduction of
                                              tax; the text says "nonnegative net
                                              liabilities", so floor at zero)

Eligibility: the itemized method "may be used only when <flag> is true" -- the literal
word before "is true" is the boolean flag value (true -> eligible, false -> not).

Selection: use itemized only if eligible AND net_itemized < net_standard (STRICTLY lower);
otherwise (tie, higher, or ineligible) use the standard method.

Outputs:
  final   = net liability of the selected method (USD, unrounded)
  slot 1  = standard taxable income  = max(0, G - D_standard)
  slot 2  = itemized taxable income  = max(0, G - D_itemized)
            (both reported regardless of eligibility / which method is selected)

No overrides of standard conventions beyond the stated rules. No intermediate rounding;
the framework applies half-up 2dp to the final answer and each checkpoint.
"""
from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F  # noqa: F401

TEMPLATE_ID = "h047"


def _flag(text: str) -> bool:
    m = re.search(r"only when\s+(\w+)\s+is\s+true", text)
    if m is None:
        raise ValueError("eligibility flag not found")
    word = m.group(1).strip().lower()
    if word in ("true", "yes"):
        return True
    if word in ("false", "no"):
        return False
    raise ValueError(f"unrecognised eligibility flag {word!r}")


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross income is {N}", text)
    rate = grab(r"tax rate is {N}", text)
    if re.search(r"tax rate is\s+-?[\d.,/]+\s*(?:percent|%)", text):
        rate = rate / 100

    d_std, c_std = grab_all(
        r"standard method permits a deduction of {N} and a credit of {N}", text
    )
    d_itm, c_itm = grab_all(
        r"itemized method permits a deduction of {N} and a credit of {N}", text
    )
    eligible = _flag(text)

    zero = Fraction(0)

    def taxable(d: Fraction) -> Fraction:
        return max(zero, gross - d)

    def net(d: Fraction, c: Fraction) -> Fraction:
        return max(zero, rate * taxable(d) - c)

    tax_inc_std = taxable(d_std)
    tax_inc_itm = taxable(d_itm)
    net_std = net(d_std, c_std)
    net_itm = net(d_itm, c_itm)

    if eligible and net_itm < net_std:
        final = net_itm
    else:
        final = net_std

    return {
        "final": final,
        "slots": {
            "standard_taxable_checkpoint": tax_inc_std,
            "itemized_taxable_checkpoint": tax_inc_itm,
        },
    }
