# h069 -- retirement-date selection by projected capital vs. date-specific requirement.
#
# FINANCE MODEL
# -------------
# * Starting capital S (existing savings) plus a one-time contribution C made TODAY (t = 0)
#   gives a combined amount P0 = S + C that is invested for the whole horizon.
# * The combined amount earns a stated annual rate r (given as a plain decimal fraction,
#   e.g. 0.02 = 2% per year, NOT a percent number), compounded ANNUALLY (standard convention,
#   no override in the text).  Growth factor to horizon n years: G(n) = (1 + r) ** n  (n integer
#   here, so exact Fraction power -- no rounding inside the computation).
# * Projected capital at a date: V(n) = P0 * G(n).
# * Each date has its own required capital R_e (earlier date) and R_l (later date), and a
#   common safety margin M.  A date is feasible only if V(n) exceeds R by AT LEAST M, i.e.
#   V(n) - R >= M  (non-strict: "at least").
# * Decision rule: prefer the earlier date whenever it is feasible; otherwise the later date
#   if feasible; otherwise neither.
#     feasible(earlier)               -> "earlier_date"
#     elif feasible(later)            -> "later_date"
#     else                            -> "neither_date"
# * "earlier"/"later" are the labels used in the text (the date labels, not a comparison of
#   the year counts: an "earlier" date could in principle carry a larger year count in the
#   text, so each slot follows its label and the horizon attached to that label).
# * Checkpoints (unrounded; framework rounds half-up to 6 dp):
#     slot 1 = G(n_earlier) = (1 + r) ** n_earlier
#     slot 2 = G(n_later)   = (1 + r) ** n_later
#   Both are plain multiples (dimensionless), independent of the decision.

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h069"


def solve(text: str, q: dict) -> dict:
    savings = grab(r"has\s+{N}\s+and can add", text)
    contribution = grab(r"contribution of\s+{N}\s+today", text)
    rate = grab(r"earns\s+{N}\s+annually", text)

    n_early, req_early = grab_all(
        r"earlier retirement in\s+{N}\s+years?\s+requires capital of\s+{N}", text
    )
    n_late, req_late = grab_all(
        r"later retirement in\s+{N}\s+years?\s+requires\s+{N}", text
    )
    margin = grab(r"by at least\s+{N}", text)

    principal = savings + contribution

    g_early = (1 + rate) ** int(n_early)
    g_late = (1 + rate) ** int(n_late)

    proj_early = principal * g_early
    proj_late = principal * g_late

    feas_early = proj_early - req_early >= margin
    feas_late = proj_late - req_late >= margin

    if feas_early:
        final = "earlier_date"
    elif feas_late:
        final = "later_date"
    else:
        final = "neither_date"

    return {
        "final": final,
        "slots": {
            "earlier_growth_factor_checkpoint": g_early,
            "later_growth_factor_checkpoint": g_late,
        },
    }
