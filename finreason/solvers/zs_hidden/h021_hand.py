"""h021: target levered beta from two comparables via zero-debt-beta Hamada (unlever / relever)."""

from fractions import Fraction

from finreason.nums import grab_all

TEMPLATE_ID = "h021"


def solve(text: str, q: dict) -> dict:
    # Comparable A: levered beta, debt, equity, tax rate
    bA, dA, eA, tA = grab_all(
        r"Comparable A has levered beta {N}, debt market value {N} USD, "
        r"common-equity market value {N} USD, and marginal corporate tax rate {N}",
        text,
    )
    # Comparable B: corresponding values (beta, debt, equity, tax)
    bB, dB, eB, tB = grab_all(
        r"Comparable B has corresponding values {N}, {N} USD, {N} USD, and {N}",
        text,
    )
    # Target: debt, equity, tax
    dT, eT, tT = grab_all(
        r"The target has debt market value {N} USD, common-equity market value {N} USD, "
        r"and tax rate {N}",
        text,
    )

    # Tax-adjusted debt term (1 - t) * D used in each Hamada factor
    adj_a = (1 - tA) * dA
    adj_b = (1 - tB) * dB
    adj_t = (1 - tT) * dT

    # Hamada factor = [E + (1 - t) D] / E ; unlevered beta = levered / factor
    fac_a = (eA + adj_a) / eA
    fac_b = (eB + adj_b) / eB
    fac_t = (eT + adj_t) / eT

    bu_a = bA / fac_a
    bu_b = bB / fac_b
    bu_mean = (bu_a + bu_b) / 2

    target_beta = bu_mean * fac_t

    return {
        "final": Fraction(target_beta),
        "slots": {
            "comparable_a_tax_adjusted_debt_checkpoint": Fraction(adj_a),
            "comparable_b_tax_adjusted_debt_checkpoint": Fraction(adj_b),
        },
    }
