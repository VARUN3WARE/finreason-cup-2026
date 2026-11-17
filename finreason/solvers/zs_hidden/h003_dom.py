# FINANCE MODEL (h003): equalising after-tax profit margins of two segments by splitting one shared deductible cost pool.
#
# Segment i in {A, B}: revenue R_i, pre-shared-cost pre-tax margin m_i (after segment-specific costs), tax rate t_i.
# Shared deductible pool S is allocated exactly once: fraction x to A, (1 - x) to B.
#   pre-tax profit_A = R_A*m_A - x*S            pre-tax profit_B = R_B*m_B - (1-x)*S
#   after-tax profit_i = (1 - t_i) * pre-tax profit_i      (tax applied to the resulting positive pre-tax profit)
#   after-tax margin_i = after-tax profit_i / R_i
# "After-tax profit margin ratios equal" => (1-t_A)(m_A - x*S/R_A) = (1-t_B)(m_B - (1-x)*S/R_B).
# Linear in x; with a = 1-t_A, b = 1-t_B:
#   a*m_A - a*x*S/R_A = b*m_B - b*S/R_B + b*x*S/R_B
#   x = (a*m_A - b*m_B + b*S/R_B) / (S*(a/R_A + b/R_B))
# Answer = 100*x (percent), unrounded; framework rounds half-up to 2 dp.
# Checkpoint 1 = S / R_A (ratio), checkpoint 2 = S / R_B (ratio) -- the shared cost burden of each segment, unrounded.
# No override of standard conventions; x is not clamped (text states no bound), positivity of profits is a stated premise.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h003"


def solve(text: str, q: dict) -> dict:
    RA = grab(r"Segment A has revenue {N}", text)
    mA = grab(r"Segment A has revenue {N}, pre-shared-cost pre-tax profit margin {N}", text, 2)
    tA = grab(r"Segment A has revenue {N}, pre-shared-cost pre-tax profit margin {N}, and tax rate {N}", text, 3)
    RB = grab(r"Segment B has revenue {N}", text)
    mB = grab(r"Segment B has revenue {N}, pre-shared-cost pre-tax profit margin {N}", text, 2)
    tB = grab(r"Segment B has revenue {N}, pre-shared-cost pre-tax profit margin {N}, and tax rate {N}", text, 3)
    S = grab(r"shared deductible cost pool of {N}", text)

    a = 1 - tA
    b = 1 - tB
    x = (a * mA - b * mB + b * S / RB) / (S * (a / RA + b / RB))
    return {
        "final": x * 100,
        "slots": {
            "segment_a_shared_cost_burden_ratio_checkpoint": S / RA,
            "segment_b_shared_cost_burden_ratio_checkpoint": S / RB,
        },
    }
