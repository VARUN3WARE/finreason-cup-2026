"""h108 -- maximum additional gross income that fits in the remaining tax budget.

LITERAL TRANSCRIPTION: every sentence of the question becomes a named variable,
definition or rule below, in the order the question states them.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, NUMBER, grab

TEMPLATE_ID = "h108"


def _rate(pattern: str, text: str) -> Fraction:
    """Number captured at {N}; a trailing 'percent'/'%' marker turns it into a ratio."""
    rx = pattern.replace("{N}", f"({NUMBER})(\\s*(?:percent|%))?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    return value / 100 if m.group(2) else value


def solve(text: str, q: dict) -> dict:
    # S1: "a taxpayer's total tax budget is B, of which C is already committed."
    total_tax_budget = grab(r"total tax budget is (?:USD\s*)?{N}", text)
    already_committed = grab(r"of which (?:USD\s*)?{N} is already committed", text)

    # S2: "Additional taxable income is charged at t, and only f of additional gross
    #      income enters the taxable base."
    tax_rate_on_additional_taxable_income = _rate(
        r"[Aa]dditional taxable income is charged at {N}", text
    )
    share_of_additional_gross_entering_taxable_base = _rate(
        r"only {N} of additional gross income enters the taxable base", text
    )

    def additional_taxable_income(additional_gross_income: Fraction) -> Fraction:
        # only f of additional gross income enters the taxable base
        return share_of_additional_gross_entering_taxable_base * additional_gross_income

    def tax_on_additional_gross_income(additional_gross_income: Fraction) -> Fraction:
        # additional taxable income is charged at t
        return tax_rate_on_additional_taxable_income * additional_taxable_income(
            additional_gross_income
        )

    def stays_within_tax_budget(additional_gross_income: Fraction) -> bool:
        # committed tax plus the tax on the additional income must not exceed the total budget
        return (
            already_committed + tax_on_additional_gross_income(additional_gross_income)
            <= total_tax_budget
        )

    # Checkpoint 1: share of the total tax budget already committed (ratio).
    committed_tax_budget_share = already_committed / total_tax_budget

    # S3: "Compute the exact maximum additional gross-income threshold that stays within
    #      the tax budget."  Tax is linear in gross income, so the maximum is where the
    #      committed amount plus the new tax exactly exhausts the total budget.
    remaining_tax_budget = total_tax_budget - already_committed
    effective_tax_per_unit_of_gross = (
        tax_rate_on_additional_taxable_income * share_of_additional_gross_entering_taxable_base
    )
    if effective_tax_per_unit_of_gross <= 0:
        raise ValueError("non-positive effective tax per unit of gross income")
    exact_maximum_threshold = remaining_tax_budget / effective_tax_per_unit_of_gross

    # S4: "Test the budget using the unrounded exact threshold" -- the exact threshold
    #      stays within the budget, and anything above it does not (so it is the maximum).
    if not stays_within_tax_budget(exact_maximum_threshold):
        raise ValueError("exact threshold breaches the tax budget")
    if stays_within_tax_budget(exact_maximum_threshold + Fraction(1, 10**12)):
        raise ValueError("threshold is not the maximum")

    # "...then report that threshold in USD rounded half up to two decimal places; the
    #  displayed amount is a reporting approximation of the exact maximum."
    # Return the unrounded exact value; the framework applies the half-up rounding.
    return {
        "final": exact_maximum_threshold,
        "slots": {"committed_tax_budget_share_checkpoint": committed_tax_budget_share},
    }
