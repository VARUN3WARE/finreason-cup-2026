# FINANCE MODEL
# -------------
# E = earnings normalized per CURRENT common share, before preferred distributions (USD / current share).
# g = ratio by which the issuance increases the common-share base  -> post-issuance share base = (1 + g) x current.
# D = preferred-dividend allocation per CURRENT common share (USD / current share), deducted from earnings.
#
# Pro forma post-issuance EPS (per post-issuance share), with the same earnings pool spread over the larger base:
#       EPS_post = (E - D) / (1 + g)
# Constraint: EPS_post >= T (target EPS floor, USD per post-issuance share).
#       (E - D) / (1 + g) >= T   <=>   D <= E - T * (1 + g)
# Maximum allocation: D_max = E - T * (1 + g), in USD per current common share (exact, no intermediate rounding).
# Checkpoint "post-issuance share-base multiple" = 1 + g (plain ratio).
# Overrides / conventions: none; "increases ... by ratio g" is read as growth factor (1 + g), not a multiple g.
# No floor at zero is applied (all instances give positive values; the text asks for the plain maximum).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h024"


def solve(text: str, q: dict) -> dict:
    e = grab(r"earnings normalized per current common share are {N}", text)
    g = grab(r"common-share base by ratio {N}", text)
    t = grab(r"at or above {N},", text)
    mult = 1 + g
    d_max = e - t * mult
    return {"final": d_max, "slots": {"dilution_multiple_checkpoint": mult}}
