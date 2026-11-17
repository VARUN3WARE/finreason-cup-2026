# h108 -- maximum additional gross income that keeps total tax within a fixed tax budget.
#
# FINANCE MODEL (written before coding)
# ---------------------------------------------------------------------------------------------
# Quantities (all in USD unless stated; rates/fractions are plain decimal fractions, NOT percents):
#   B  = total tax budget                      ("total tax budget is B")
#   C  = tax already committed out of B        ("of which C is already committed"), 0 <= C <= B
#   r  = marginal rate charged on ADDITIONAL TAXABLE income    ("charged at r")      -> 0.8 means 80%
#   f  = share of ADDITIONAL GROSS income that enters the taxable base ("only f of additional gross
#        income enters the taxable base")                                              -> 0.6 means 60%
#   G  = additional gross income (the unknown threshold)
#
# Mechanics:
#   additional taxable income  T = f * G              (only a fraction f of gross income is taxable)
#   additional tax             = r * T = r * f * G     (the marginal rate applies to the taxable part)
#   total tax after G          = C + r * f * G         (committed tax is already part of the budget B)
#   "stays within the tax budget"  <=>  C + r * f * G <= B   (non-strict: within = at most B)
#
# Maximum G (the "exact maximum additional gross-income threshold"):
#   G* = (B - C) / (r * f)         -- the tax bill at G* equals B exactly; any larger G exceeds B.
#   "Test the budget using the unrounded exact threshold" -> the budget test is done at the exact
#   rational G* (where total tax == B, so it is within budget). The reported figure is only the
#   half-up 2-dp display of G* (the framework applies the result_spec rounding), so we return the
#   UNROUNDED exact Fraction G*. We must NOT floor/round G* to cents before using it, and must NOT
#   shrink the answer so that a rounded figure re-tests within budget: the text says the displayed
#   amount is "a reporting approximation of the exact maximum".
#
# Checkpoint (position 1): committed_tax_budget_share_checkpoint
#   "share of the total tax budget already committed" = C / B, a plain ratio (6 dp half up applied
#   by the framework to the unrounded exact C / B).
#
# Conventions / overrides noted:
#   * r and f are given as decimals (0.8, 0.6) and used as-is (no division by 100).
#   * No floor at zero is stated, so the closed form is used as worded (all instances have B > C,
#     so G* > 0 anyway).
#   * No brackets, no phase-outs, no rounding of any intermediate quantity is stated -> none applied.
#   * Exact tie handling (e.g. G* = x.xx5 exactly) is left to the framework's half-up rendering.

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h108"


def solve(text: str, q: dict) -> dict:
    # --- parse inputs, anchored on the surrounding words ---------------------------------------
    budget = grab(r"total tax budget is {N}", text)                    # B
    committed = grab(r"of which {N} is already committed", text)       # C
    rate = grab(r"charged at {N}", text)                               # r (decimal fraction)
    base_share = grab(r"only {N} of additional gross income", text)   # f (decimal fraction)

    # --- model ----------------------------------------------------------------------------------
    committed_share = committed / budget                      # C / B   (checkpoint, ratio)
    remaining_budget = budget - committed                     # B - C   (tax room left)
    marginal_burden = rate * base_share                       # r * f   (tax per USD of additional gross income)
    threshold = remaining_budget / marginal_burden            # G* = (B - C) / (r * f)

    # sanity: at the exact threshold the total tax equals the budget (within budget, non-strict)
    assert committed + marginal_burden * threshold == budget

    return {
        "final": threshold,
        "slots": {
            "committed_tax_budget_share_checkpoint": committed_share,
        },
    }
