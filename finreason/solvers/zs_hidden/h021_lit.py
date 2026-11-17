"""h021 -- target levered beta from two equally weighted comparables (zero-debt-beta Hamada).

Literal transcription of the question text.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h021"

N = "{N}"


def solve(text: str, q: dict) -> dict:
    # "Comparable A has levered beta X, debt market value D USD, common-equity market value E USD,
    #  and marginal corporate tax rate t."
    beta_a, debt_a, equity_a, tax_a = grab_all(
        r"Comparable A has levered beta {N}, debt market value {N} USD, "
        r"common-equity market value {N} USD, and marginal corporate tax rate {N}",
        text,
    )
    # "Comparable B has corresponding values X, D USD, E USD, and t."
    beta_b, debt_b, equity_b, tax_b = grab_all(
        r"Comparable B has corresponding values {N}, {N} USD, {N} USD, and {N}", text
    )
    # "The target has debt market value D USD, common-equity market value E USD, and tax rate t."
    debt_t, equity_t, tax_t = grab_all(
        r"The target has debt market value {N} USD, common-equity market value {N} USD, "
        r"and tax rate {N}",
        text,
    )

    # Tax rates may be stated as decimals (0.2) -- if stated as "percent" convert.
    def rate(x: Fraction) -> Fraction:
        return x / 100 if x > 1 else x

    tax_a, tax_b, tax_t = rate(tax_a), rate(tax_b), rate(tax_t)

    # "For each comparable, divide observed levered beta by
    #  [equity plus (one minus tax rate) times debt] divided by equity."
    tax_adj_debt_a = (1 - tax_a) * debt_a
    tax_adj_debt_b = (1 - tax_b) * debt_b
    factor_a = (equity_a + tax_adj_debt_a) / equity_a
    factor_b = (equity_b + tax_adj_debt_b) / equity_b
    unlev_a = beta_a / factor_a
    unlev_b = beta_b / factor_b

    # "Take the unweighted arithmetic mean of the two unlevered betas,
    #  then multiply by the target company's factor of the same form."
    mean_unlev = (unlev_a + unlev_b) / 2
    tax_adj_debt_t = (1 - tax_t) * debt_t
    factor_t = (equity_t + tax_adj_debt_t) / equity_t
    target_beta = mean_unlev * factor_t

    return {
        "final": target_beta,
        "slots": {
            "comparable_a_tax_adjusted_debt_checkpoint": tax_adj_debt_a,
            "comparable_b_tax_adjusted_debt_checkpoint": tax_adj_debt_b,
        },
    }
