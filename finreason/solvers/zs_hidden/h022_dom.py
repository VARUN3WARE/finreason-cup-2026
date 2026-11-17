# FINANCE MODEL (h022): post-earnout ownership of target sellers in the acquirer's common-share base.
#
# Everything is valued at ONE fixed contractual share price, so share counts are proportional to USD value
# and ownership can be computed in value terms (shares = value / price; the price cancels).
#
#   V   = aggregate reference equity value of the acquirer's PRE-DEAL common shares (the legacy share base).
#   B   = upfront base consideration (excludes the earnout).
#   c   = fraction of B paid in cash (c = 0.2 means 20% cash); the remainder (1 - c) is paid in acquirer stock.
#   S_u = B * (1 - c)           upfront consideration settled in common shares (USD million)  -> checkpoint 1
#   E   = earnout settlement value, fully realized, incremental to B, settled entirely in common shares
#         at the same unchanged price.
#   Sellers' shares (value terms) = S_u + E     (they retain all upfront shares; earnout shares are added)
#   Post-settlement common-share base = V + S_u + E   (no other issuance, repurchase, disposal, option
#         exercise, conversion or price adjustment)
#   Ownership % = 100 * (S_u + E) / (V + S_u + E)
#
# Conventions / overrides: none. The pre-deal value V does NOT already include the upfront shares
# ("predeal"), so the new shares dilute V. Cash portion plays no role in ownership.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h022"


def solve(text: str, q: dict) -> dict:
    V = grab(r"aggregate reference equity value\s+{N}", text)
    B = grab(r"Upfront base consideration is\s+{N}", text)
    c = grab(r"{N}\s+of that base is paid in cash", text)
    E = grab(r"settlement value\s+{N}", text)

    S_u = B * (1 - c)
    sellers = S_u + E
    base = V + sellers
    own = Fraction(100) * sellers / base
    return {"final": own, "slots": {"upfront_stock_consideration_checkpoint": S_u}}
