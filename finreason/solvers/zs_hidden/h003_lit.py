"""h003: shared deductible cost pool split so two segments' after-tax margins are equal.

Literal transcription of the question, sentence by sentence.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h003"


def solve(text: str, q: dict) -> dict:
    # "Segment A has revenue R_A, pre-shared-cost pre-tax profit margin m_A, and tax rate t_A."
    rev_a = grab(r"Segment A has revenue {N}", text)
    margin_a = grab(r"Segment A has revenue [^,]*, pre-shared-cost pre-tax profit margin {N}", text)
    tax_a = grab(r"Segment A has revenue .*?and tax rate {N}", text)
    # "Segment B has revenue R_B, pre-shared-cost pre-tax profit margin m_B, and tax rate t_B."
    rev_b = grab(r"Segment B has revenue {N}", text)
    margin_b = grab(r"Segment B has revenue [^,]*, pre-shared-cost pre-tax profit margin {N}", text)
    tax_b = grab(r"Segment B has revenue .*?and tax rate {N}", text)
    # "These margins are after all segment-specific operating costs but before allocating
    #  one shared deductible cost pool of S."
    pool = grab(r"shared deductible cost pool of {N}", text)

    # Pre-shared-cost pre-tax profit of each segment = revenue x margin.
    pre_a = rev_a * margin_a
    pre_b = rev_b * margin_b

    # "Allocate fraction x of that pool to A and the complementary fraction to B exactly once."
    # "each tax rate is applied to the resulting positive pre-tax profit" -> tax on max(0, profit).
    def after_tax_margin_a(x: Fraction) -> Fraction:
        pt = pre_a - x * pool
        tax = tax_a * pt if pt > 0 else Fraction(0)
        return (pt - tax) / rev_a

    def after_tax_margin_b(x: Fraction) -> Fraction:
        pt = pre_b - (1 - x) * pool
        tax = tax_b * pt if pt > 0 else Fraction(0)
        return (pt - tax) / rev_b

    # f(x) = margin_A(x) - margin_B(x) is continuous, piecewise linear and strictly decreasing
    # in x. Solve exactly within each tax regime (A taxed or not, B taxed or not) and keep the
    # root consistent with its regime.
    root = None
    for ka in (1 - tax_a, Fraction(1)):
        for kb in (1 - tax_b, Fraction(1)):
            # ka*(pre_a - x*pool)/rev_a = kb*(pre_b - pool + x*pool)/rev_b
            ca = ka / rev_a
            cb = kb / rev_b
            x = (ca * pre_a - cb * (pre_b - pool)) / (pool * (ca + cb))
            # Keep it only if the true (regime-aware) margins are equal at x.
            if after_tax_margin_a(x) == after_tax_margin_b(x):
                root = x
                break
        if root is not None:
            break
    if root is None:
        raise ValueError("no consistent allocation found")

    # Checkpoints: shared cost pool as a ratio of each segment's revenue.
    burden_a = pool / rev_a
    burden_b = pool / rev_b

    # "What percentage x of the shared cost pool must be allocated to A ..." -> percent.
    final = root * 100

    return {
        "final": final,
        "slots": {
            "segment_a_shared_cost_burden_ratio_checkpoint": burden_a,
            "segment_b_shared_cost_burden_ratio_checkpoint": burden_b,
        },
    }
