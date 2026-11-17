"""h047 -- standard vs itemized tax method: taxable income, nonnegative net liability, choose lower.

AMBIGUITY RESOLUTIONS (skeptical pass)
--------------------------------------
A1. Tax rate unit.  "the tax rate is 0.3" carries no "percent" word, so it is a plain
    ratio (0.3 = 30%).  Sanity: credits of ~1000-2000 are only meaningful against a
    tax of ~20,000 (= 0.3 * 80,679), not against 0.3% * 80,679 = 242.  A "percent"/"%"
    suffix is still honoured defensively (divide by 100) if it ever appears.
A2. Deduction vs credit.  A *deduction* reduces income: taxable = gross - deduction.
    A *credit* reduces the tax: net liability = taxable * rate - credit.  The slots are
    literally named "taxable income under the <method>", which pins the deduction to
    the income line and leaves the credit for the liability line.
A3. Floor at zero.  "Compute both NONNEGATIVE net liabilities" -> liability =
    max(0, taxable * rate - credit).  No floor is stated for taxable income itself, so
    none is applied ("apply only the rules stated").  Irrelevant on all 3 instances
    (deductions are far below gross income) and the final answer is identical either
    way because the liability floor absorbs a negative taxable income.
A4. Eligibility token.  "may be used only when false is true" -> NOT eligible;
    "when true is true" -> eligible.  Implemented as (word1 == word2) over
    {true,false}, which also covers a hypothetical "false is false".
A5. Selection rule.  "use the itemized method only when eligible AND STRICTLY lower;
    otherwise use the standard method" -> itemized iff eligible and
    item_liab < std_liab (strict).  Ties -> standard.  The comparison is made on the
    nonnegative (floored) liabilities, as the sentence orders ("Compute both
    nonnegative net liabilities and use ...").
A6. Checkpoints.  "Compute both" -> both taxable incomes are reported regardless of
    eligibility or which method wins:
      standard_taxable_checkpoint = gross - standard deduction   (usd)
      itemized_taxable_checkpoint = gross - itemized deduction   (usd)
A7. Rounding.  No sentence reuses a rounded/whole-unit figure, so every value is
    returned exact; the framework rounds half-up to 2 dp.
A8. Final.  "What tax liability is payable?" = the chosen method's nonnegative net
    liability (usd).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab

TEMPLATE_ID = "h047"

_NUM = r"(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?(?:/\d+)?)"


def _rate(text: str) -> Fraction:
    """Tax rate as a ratio; tolerate an optional percent suffix (A1)."""
    m = re.search(r"tax rate is (?:USD\s*)?" + _NUM + r"\s*(percent|%)?", text, flags=re.S | re.I)
    if m is None:
        raise ValueError("tax rate not found")
    r = F(m.group(1))
    if m.group(2):
        r /= 100
    return r


def _eligible(text: str) -> bool:
    """'may be used only when X is Y' -> eligible iff X == Y (A4)."""
    m = re.search(r"only when\s+(true|false)\s+is\s+(true|false)", text, flags=re.I)
    if m is None:
        raise ValueError("eligibility condition not found")
    return m.group(1).lower() == m.group(2).lower()


def _method(text: str, name: str) -> tuple[Fraction, Fraction]:
    """(deduction, credit) for the named method."""
    ded = grab(name + r" method permits a deduction of (?:USD\s*)?{N}", text)
    cred = grab(name + r" method permits a deduction of (?:USD\s*)?{N} and a credit of (?:USD\s*)?{N}", text, group=2)
    return ded, cred


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross income is (?:USD\s*)?{N}", text)
    rate = _rate(text)
    std_ded, std_cred = _method(text, "standard")
    item_ded, item_cred = _method(text, "itemized")
    eligible = _eligible(text)

    zero = Fraction(0)

    # A2 / A6: taxable income per method (exact, no floor stated).
    std_taxable = gross - std_ded
    item_taxable = gross - item_ded

    # A2 / A3: nonnegative net liabilities.
    std_liab = max(zero, std_taxable * rate - std_cred)
    item_liab = max(zero, item_taxable * rate - item_cred)

    # A5: itemized only when eligible AND strictly lower; otherwise standard.
    use_itemized = eligible and item_liab < std_liab
    payable = item_liab if use_itemized else std_liab

    return {
        "final": payable,
        "slots": {
            "standard_taxable_checkpoint": std_taxable,
            "itemized_taxable_checkpoint": item_taxable,
        },
    }
