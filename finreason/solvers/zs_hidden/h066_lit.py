"""h066 -- ESG project: maximum initial investment meeting a required ROI ratio.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h066"


def solve(text: str, q: dict) -> dict:
    # S1: "An ESG project is expected to produce annual energy savings of E and
    #      annual water savings of W, while requiring annual maintenance cost of M."
    energy_savings = grab(r"annual energy savings of {N}", text)
    water_savings = grab(r"annual water savings of {N}", text)
    maintenance_cost = grab(r"annual maintenance cost of {N}", text)

    # Recurring net benefit per year = savings minus maintenance.
    annual_net_benefit = energy_savings + water_savings - maintenance_cost

    # S2: "The full-horizon present-value multiplier for these recurring net benefits is K."
    pv_multiplier = grab(r"present-value multiplier for these recurring net benefits is {N}", text)
    pv_net_benefits = annual_net_benefit * pv_multiplier

    # S3: "Using ROI = (PV of net benefits minus initial investment) / initial investment,
    #      compute the maximum initial investment that exactly meets the required ROI ratio R."
    required_roi = grab(r"required ROI ratio {N}", text)
    # (PV - I) / I = R  =>  PV = I (1 + R)  =>  I = PV / (1 + R)
    # ROI is decreasing in I (for PV > 0), so the I that exactly meets R is the maximum.
    max_initial_investment = pv_net_benefits / (1 + required_roi)

    return {
        "final": Fraction(max_initial_investment),
        "slots": {"annual_net_benefit_checkpoint": Fraction(annual_net_benefit)},
    }
