# h105 -- social-impact program: beneficiary-equivalent scale that exactly meets a surplus requirement.
#
# ---------------------------------------------------------------------------------------------------------------
# FINANCE MODEL (written before the code)
# ---------------------------------------------------------------------------------------------------------------
# Economic setting
#   A social-impact program carries two lump-sum, scale-independent (fixed) cost lines, both in USD:
#       L = launch cost            (given: "launch cost {N}")
#       M = monitoring cost        (given: "monitoring cost {N}")
#   Combined fixed costs:          C = L + M                      (text: "combined fixed costs")
#
#   Each "beneficiary-equivalent unit" generates NET monetized social value v (USD per unit)
#       v = given ("net monetized social value {N}"); "net" means it is already after any per-unit cost, so there
#       is NO further variable-cost deduction, no discounting, no tax, no time value -- the text applies none.
#   Total social value at scale n (n = number of beneficiary-equivalent units, a plain count):
#       V(n) = n * v                                              (text: "scale multiplied by value per unit")
#
#   Investor hurdle ("surplus ratio" s, a plain ratio -- 0.1 means 10 percent, NOT 0.1 percent):
#       V must exceed C by the surplus ratio:   V - C = s * C     (surplus S = s * C, expressed as a fraction of costs)
#       => required social value  R = C * (1 + s)                 (text states this equivalence explicitly)
#
#   Break-even-with-surplus scale ("exactly meets this requirement", i.e. V(n*) = R, equality, no rounding of n):
#       n* = R / v = (L + M) * (1 + s) / v                        -> FINAL ANSWER, unit `count`, half-up 2 dp
#       (the scale is NOT rounded up to a whole unit: the text says "exactly meets" and the answer is a 2-dp decimal)
#
# Checkpoint (slot monitoring_surplus_value_checkpoint, USD, half-up 2 dp)
#   "the surplus requirement attributable to monitoring cost"
#   The required surplus is S = s * C = s * L + s * M, i.e. it splits additively across the two cost lines; the part
#   of the surplus requirement that is caused by (attributable to) the monitoring cost line is
#       S_M = s * M                                               (USD; exact, unrounded)
#   It is the monitoring-cost share of the surplus ONLY (cost itself, M, is not included; "one plus s" is not used
#   here because that would be the monitoring share of required value R_M = M * (1 + s), which is a different
#   quantity -- the checkpoint names the *surplus*, not the required value).
#
# Overrides of standard conventions: none.  Everything is the plain-ratio, single-period, undiscounted arithmetic
# that the text spells out.  All arithmetic exact (Fraction); the framework applies each result_spec's rounding.
# Numbers are parsed by anchoring on the surrounding words (never by position / case id).
# ---------------------------------------------------------------------------------------------------------------

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401  (contract imports)

TEMPLATE_ID = "h105"


def solve(text: str, q: dict) -> dict:
    # --- inputs (anchored on the words around each number) -------------------------------------------------------
    launch_cost = grab(r"launch cost {N}", text)                       # L, USD
    monitoring_cost = grab(r"monitoring cost {N}", text)               # M, USD
    value_per_unit = grab(r"net monetized social value {N}", text)     # v, USD per beneficiary-equivalent unit
    surplus_ratio = grab(r"surplus ratio {N}", text)                   # s, plain ratio

    if value_per_unit == 0:
        raise ValueError("value per unit is zero; scale undefined")

    # --- model ---------------------------------------------------------------------------------------------------
    combined_fixed_costs = launch_cost + monitoring_cost               # C = L + M
    required_social_value = combined_fixed_costs * (1 + surplus_ratio)  # R = C * (1 + s)
    scale = required_social_value / value_per_unit                     # n* such that n* * v = R

    monitoring_surplus = monitoring_cost * surplus_ratio               # S_M = s * M  (monitoring share of surplus)

    return {
        "final": scale,
        "slots": {
            "monitoring_surplus_value_checkpoint": monitoring_surplus,
        },
    }
