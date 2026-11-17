# h066 -- ESG project: maximum initial investment meeting a required ROI ratio.
#
# FINANCE MODEL
#   Annual net benefit (recurring)  B  = energy savings + water savings - annual maintenance cost
#       (maintenance is a recurring cost that offsets the savings; this is the checkpoint
#        "annual savings after maintenance", in USD).
#   Present value of net benefits   PV = M * B,  M = "full-horizon present-value multiplier"
#       (a plain dimensionless multiplier that already embeds the discounting over the whole
#        horizon; no further discounting is applied).
#   ROI definition (given in text)  ROI = (PV - I) / I,  I = initial investment (> 0).
#   Required ROI ratio R is a plain ratio (1 means 100%), NOT a percent.
#   "Maximum initial investment that exactly meets the required ROI ratio":
#       (PV - I) / I = R   =>   PV = I * (1 + R)   =>   I = PV / (1 + R).
#       Any larger investment yields ROI < R, so this I is the maximum acceptable one.
#   Final answer = I in USD (unrounded exact Fraction; framework rounds half-up to 2 dp).
#
# Overrides of standard conventions: none.

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h066"


def solve(text: str, q: dict) -> dict:
    energy = grab(r"annual energy savings of {N}", text)
    water = grab(r"annual water savings of {N}", text)
    maint = grab(r"annual maintenance cost of {N}", text)
    mult = grab(r"present-value multiplier for these recurring net benefits is {N}", text)
    roi = grab(r"required ROI ratio {N}", text)

    net_annual = energy + water - maint
    pv = mult * net_annual
    invest = pv / (1 + roi)

    return {
        "final": invest,
        "slots": {"annual_net_benefit_checkpoint": net_annual},
    }
