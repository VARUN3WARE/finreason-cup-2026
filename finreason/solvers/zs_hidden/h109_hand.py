"""h109: minimum inventory carrying amount to sell so the quick ratio reaches 1 + uplift exactly.

Selling carrying amount X recovers cash C = r * X (r = net recovery rate).  Fraction f of C stays in
quick assets, the complementary fraction (1 - f) repays current liabilities at par:

    post quick assets      QA + f * C
    post current liabs     CL - (1 - f) * C
    target                 (QA + f C) / (CL - (1 - f) C) = R,   R = 1 + uplift

    => C * (f + R (1 - f)) = R * CL - QA

Each recovered dollar closes the gap R*CL - QA by f (retained cash) plus R*(1 - f): the repaid
(1 - f) lowers the quick assets required at the target ratio by R per dollar.  R*(1 - f) is the
target-weighted liability-repayment contribution (checkpoint).  Then X = C / r.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h109"


def solve(text: str, q: dict) -> dict:
    quick_assets = grab(r"has (?:USD )?{N} (?:USD )?of quick assets excluding inventory", text)
    liabilities = grab(r"and (?:USD )?{N} (?:USD )?of current liabilities", text)
    uplift = grab(r"one plus positive uplift ratio {N}", text)
    recovery = grab(r"net recovery rate {N} of carrying amount", text)
    retained = grab(r"Fraction {N} of the recovered cash remains in quick assets", text)

    target = 1 + uplift
    repaid = 1 - retained  # complementary fraction repays current liabilities at par

    liability_relief_weight = target * repaid  # target-weighted liability-repayment contribution
    gap = target * liabilities - quick_assets  # quick-asset shortfall at the target ratio
    cash_needed = gap / (retained + liability_relief_weight)
    carrying = cash_needed / recovery

    # Sanity: the exact post-transaction ratio equals the target, liabilities stay positive.
    post_qa = quick_assets + retained * cash_needed
    post_cl = liabilities - repaid * cash_needed
    assert post_cl > 0 and post_qa / post_cl == target

    return {
        "final": Fraction(carrying),
        "slots": {"liability_relief_weight_checkpoint": Fraction(liability_relief_weight)},
    }
