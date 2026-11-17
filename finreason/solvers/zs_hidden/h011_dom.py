# FINANCE MODEL (h011): net economic exposure of an investor in an issuer's shares.
#
#   derivative_equivalent_shares = derivative_reference_shares * delta
#       (the derivative "notional equivalent to X shares" is the reference share count; delta-adjusting
#        it converts the derivative into its share-equivalent exposure; this is checkpoint 1, in shares)
#   gross_long = direct_long + attributed_through_related_holdings + derivative_equivalent_shares
#   net_exposure_shares = gross_long - short_hedge          (signed; NOT floored at zero, may be negative)
#   net_exposure_pct = net_exposure_shares / shares_outstanding * 100      (percent)
#
# Conventions / overrides: none beyond the text. Fractional share counts allowed (no whole-share rounding is
# stated). Sign is preserved: a short hedge larger than long exposure yields a negative percentage.
# The final answer and the checkpoint are returned unrounded; the framework applies half-up 2dp
# independently to each (checkpoint is never fed into the final from its rounded display).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h011"


def solve(text: str, q: dict) -> dict:
    direct = grab(r"has {N} direct long shares", text)
    attributed = grab(r"{N} shares attributed through related holdings", text)
    deriv_ref = grab(r"derivative notional equivalent to {N} shares", text)
    delta = grab(r"exposure delta {N}", text)
    short = grab(r"also has {N} shares of offsetting short exposure", text)
    outstanding = grab(r"issuer has {N} shares outstanding", text)

    deriv_equiv = deriv_ref * delta
    net_shares = deriv_equiv + direct + attributed - short
    pct = net_shares / outstanding * 100

    return {"final": pct, "slots": {"derivative_equivalent_checkpoint": deriv_equiv}}
