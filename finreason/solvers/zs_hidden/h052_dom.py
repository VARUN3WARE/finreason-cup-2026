# FINANCE MODEL (h052)
# Cost-savings decomposition. Combined annual savings = energy savings + waste savings.
#   energy_savings = energy_expenditure * energy_reduction_ratio          (USD; checkpoint 1)
#   waste_savings  = combined_target - energy_savings                     (USD, residual needed)
#   waste_rate     = waste_savings / waste_expenditure * 100              (percent; final answer)
# Conventions: "achieved energy-reduction ratio" is a plain fraction of energy expenditure (0.2 = 20%),
# not a percent. The target is a combined total across both cost lines. The reduction rate is measured
# against the waste-management expenditure base. No rounding inside the chain; the framework rounds
# the final value (percent, 2 dp) and the checkpoint (usd, 2 dp). No overrides of standard conventions.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h052"


def solve(text: str, q: dict) -> dict:
    energy = grab(r"annual energy expenditure {N}", text)
    ratio = grab(r"energy-reduction ratio {N}", text)
    waste = grab(r"waste-management expenditure is {N}", text)
    target = grab(r"combined annual savings target {N}", text)

    energy_savings = energy * ratio
    waste_savings = target - energy_savings
    rate_pct = waste_savings / waste * 100

    return {"final": rate_pct, "slots": {"energy_savings_checkpoint": energy_savings}}
