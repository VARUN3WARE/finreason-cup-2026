# FINANCE MODEL (h042): expected net merchant proceeds on a primary/backup payment-retry waterfall.
#
# Inputs (per instance):
#   N   = number of original payment attempts          ("has N original payment attempts")
#   A   = stated amount per order                       ("each for A")
#   p   = primary success probability
#   q   = backup CONDITIONAL success probability (given a primary failure)
#   r1, f1 = primary variable rate (fraction of amount) and fixed fee, charged on EVERY original attempt
#   r2, f2 = backup  variable rate and fixed fee, charged on EVERY retry (retry happens only after a primary failure)
#   h1  = handling cost per primary failure
#   h2  = ADDITIONAL handling cost per order where both attempts fail (on top of h1, which that order also incurs)
#   S   = one-off subscription / batch fee, paid once
#
# Probability tree per original attempt (expectations are exact, no sampling):
#   primary success                : p
#   primary fail -> backup success : (1-p) q          <- "retry success fraction" (fraction of ORIGINAL attempts)
#   primary fail -> backup fail    : (1-p) (1-q)      <- terminal failure
#   retries per original attempt   : (1-p)
#
# Expected values (all over the N original attempts):
#   settled orders        = N [ p + (1-p) q ]           (one settlement of A if either attempt succeeds; none if both fail;
#                                                        no order retried more than once)
#   revenue               = A * settled orders
#   primary fees          = N (r1 A + f1)               (every original attempt, success or fail)
#   backup fees           = N (1-p) (r2 A + f2)         (every retry, success or fail)
#   failure handling      = h1 * N (1-p)                (every primary failure)
#   terminal extra cost   = h2 * N (1-p)(1-q)           (additional, only both-fail orders)
#   subscription          = S                           (once, not per attempt)
#   net proceeds          = revenue - primary fees - backup fees - failure handling - terminal extra - S
#
# Checkpoints:
#   1. retry_success_fraction  = (1-p) q                (ratio, 4 dp)
#   2. backup_processing_fees  = N (1-p)(r2 A + f2)     (USD)
#   3. terminal_failure_cost   = h2 * N (1-p)(1-q)      (USD; the "additional" handling for both-fail orders only,
#                                                        the per-primary-failure handling h1 is NOT part of it)
#
# Conventions / overrides: none; "fixed fee" is in USD per charged attempt; rates are plain fractions (0.02 = 2%).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h042"


def solve(text: str, q: dict) -> dict:
    N = grab(r"has {N} original payment attempts", text)
    A = grab(r"original payment attempts, each for {N}", text)
    p = grab(r"primary processor succeeds with probability {N}", text)
    qb = grab(r"conditional success probability is {N}", text)

    r1, f1 = grab_all(r"primary charges {N} of the stated amount plus fixed fee {N}", text)
    r2, f2 = grab_all(r"backup charges {N} of the stated amount plus fixed fee {N}", text)

    h1 = grab(r"incurs {N} for every primary failure", text)
    h2 = grab(r"additional {N} for every order where both attempts fail", text)
    S = grab(r"pays {N} once for the batch", text)

    fail = 1 - p
    settled_frac = p + fail * qb
    revenue = N * A * settled_frac
    primary_fees = N * (r1 * A + f1)
    backup_fees = N * fail * (r2 * A + f2)
    failure_handling = h1 * N * fail
    terminal_cost = h2 * N * fail * (1 - qb)

    net = revenue - primary_fees - backup_fees - failure_handling - terminal_cost - S

    return {
        "final": net,
        "slots": {
            "retry_success_fraction_checkpoint": fail * qb,
            "backup_processing_fees_checkpoint": backup_fees,
            "terminal_failure_cost_checkpoint": terminal_cost,
        },
    }
