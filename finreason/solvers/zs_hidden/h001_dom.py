# FINANCE MODEL (h001): maximum short-term borrowing consistent with a required current ratio.
#
#   CA  = current assets (USD mm), CL = current liabilities (USD mm)
#   P   = cash-funded non-current-asset purchase; reduces CA (cash -> fixed asset), CL unchanged
#   CA' = CA - P                      (post-purchase current assets)  <- checkpoint slot
#   R   = 1 + k, k = the stated "ratio" (0.4 / 0.8 ...), required current ratio = 1 + k
#   Borrowing x of new short-term debt: cash +x (so CA' + x) and CL + x.
#   Exactly meeting the requirement:   (CA' + x) / (CL + x) = R
#       => CA' + x = R*CL + R*x   => x = (CA' - R*CL) / (R - 1)
#   Because R > 1, extra borrowing pushes the ratio DOWN toward 1, so the ratio is a
#   decreasing function of x; the largest x keeping ratio >= R is exactly the equality point.
#   Hence the "maximum additional borrowing" = (CA' - R*CL)/(R - 1) = (CA' - R*CL)/k.
#   If the post-purchase ratio were already below R, no non-negative borrowing could
#   satisfy it; the capacity is floored at zero (not triggered in the given instances).
#   No rounding inside the computation; framework rounds to 2 dp half-up (USD million).
#   Overrides of standard convention: none ("one plus the ratio k" read literally as 1 + k).
from fractions import Fraction
import re
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h001"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"current assets of {N} and", text)
    cl = grab(r"current liabilities of {N} in USD millions", text)
    purchase = grab(r"non-current-asset purchase of {N}", text)
    k = grab(r"one plus the ratio {N}", text)

    ca_post = ca - purchase
    req = 1 + k
    x = (ca_post - req * cl) / (req - 1)
    if x < 0:
        x = Fraction(0)
    return {"final": x, "slots": {"post_purchase_assets_checkpoint": ca_post}}
