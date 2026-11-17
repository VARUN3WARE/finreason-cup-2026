# FINANCE MODEL (h035) -- crypto price shock with threshold-selected support policy
#
#   P0  : initial price per token (USD)
#   L   : fraction of price lost in the shock (loss ratio)
#   retention = 1 - L                      (share of initial price retained; checkpoint 1, ratio)
#   P1  = P0 * (1 - L)                     (post-shock price)
#   Policy selection: severe if L >= threshold (AT LEAST, inclusive, exact comparison on
#                     rationals -- no rounding of L or threshold), else mild.
#   Chosen policy has support ratio s and per-token deduction d:
#   P2  = P1 * (1 + s) - d                 (support increases post-shock price by ratio s FIRST,
#                                           THEN the USD deduction is subtracted)
#   Final answer = P2 in USD, rounded half-up to 2 dp only at the end by the framework.
#
# Conventions / overrides: none; no floor at zero stated, so a negative net price is kept as is.
# All arithmetic in exact Fractions; loss ratio may be given as a rational (1/3) or decimal.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h035"


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"starts at {N} USD per token", text)
    loss = grab(r"loses fraction {N} of its price", text)
    thr = grab(r"loss ratio is at least {N};", text)
    s_sev = grab(r"severe policy increases the post-shock price by support ratio {N}", text)
    d_sev = grab(r"support ratio " + r"-?\d+(?:\.\d+)?(?:/\d+)? and then deducts {N} USD", text)
    s_mild = grab(r"mild policy increases it by support ratio {N}", text)
    # deduction following the mild support ratio
    d_mild = grab(r"mild policy increases it by support ratio -?\d+(?:\.\d+)?(?:/\d+)? and then deducts {N} USD", text)

    retention = 1 - loss
    post = p0 * retention
    if loss >= thr:
        s, d = s_sev, d_sev
    else:
        s, d = s_mild, d_mild
    net = post * (1 + s) - d
    return {"final": net, "slots": {"post_shock_retention_checkpoint": retention}}
