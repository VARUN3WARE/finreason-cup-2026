"""h047 -- standard vs itemized tax method choice (literal transcription).

Sentence by sentence:
  1. gross income is G and the tax rate is r.
  2. The standard method permits a deduction of Ds and a credit of Cs.
  3. The itemized method permits a deduction of Di and a credit of Ci, but it may be
     used only when <A> is <B>  (eligible iff the two boolean tokens agree).
  4. Compute both nonnegative net liabilities:
        taxable_m  = G - D_m
        liability_m = max(0, taxable_m * r - C_m)
     Use the itemized method only when eligible AND strictly lower; otherwise standard.
  5. Final = the payable liability of the chosen method.
Checkpoints: taxable income under standard (G - Ds) and under itemized (G - Di).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h047"


def _bool(tok: str) -> bool:
    t = tok.strip().lower()
    if t in ("true", "yes"):
        return True
    if t in ("false", "no"):
        return False
    raise ValueError(f"unrecognised boolean token {tok!r}")


def solve(text: str, q: dict) -> dict:
    # Sentence 1: gross income and tax rate.
    gross = grab(r"gross income is {N}", text)
    m = re.search(rf"tax rate is ({NUMBER})(\s*(?:percent|%))?", text)
    if m is None:
        raise ValueError("tax rate not found")
    rate = F(m.group(1))
    if m.group(2):
        rate = rate / 100

    # Sentence 2: standard method.
    std_ded = grab(r"standard method permits a deduction of {N}", text)
    std_cred = grab(r"standard method permits a deduction of {N} and a credit of {N}", text, group=2)

    # Sentence 3: itemized method and its eligibility condition.
    itm_ded = grab(r"itemized method permits a deduction of {N}", text)
    itm_cred = grab(r"itemized method permits a deduction of {N} and a credit of {N}", text, group=2)
    cond = re.search(r"may be used only when\s+(\w+)\s+is\s+(\w+)", text)
    if cond is None:
        raise ValueError("eligibility condition not found")
    eligible = _bool(cond.group(1)) == _bool(cond.group(2))

    # Sentence 4: taxable incomes and nonnegative net liabilities.
    std_taxable = gross - std_ded
    itm_taxable = gross - itm_ded
    std_liab = max(Fraction(0), std_taxable * rate - std_cred)
    itm_liab = max(Fraction(0), itm_taxable * rate - itm_cred)

    # Itemized only when eligible and strictly lower; otherwise standard.
    if eligible and itm_liab < std_liab:
        payable = itm_liab
    else:
        payable = std_liab

    return {
        "final": payable,
        "slots": {
            "standard_taxable_checkpoint": std_taxable,
            "itemized_taxable_checkpoint": itm_taxable,
        },
    }
