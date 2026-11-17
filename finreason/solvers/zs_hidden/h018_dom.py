# FINANCE MODEL (h018): three-stage sequential common-share issuance, accretion/dilution screen.
#
# Quantities (all per CURRENT share, i.e. per share outstanding before any issuance):
#   E   = current common EPS (current earnings per current share).
#   a_X = total earnings ADDED by option X per current share (the "total" refers to the sum over
#         all three stages; it is incremental to current earnings, so pro forma earnings per
#         current share = E + a_X).
#   r_X = per-stage share-base increase ratio; the same ratio applies at each of the 3 stages, so
#         one stage multiplies the share base by (1 + r_X) and the cumulative share multiple is
#         M_X = (1 + r_X)^3  (explicitly given in the text; integer power -> exact Fraction).
#   Pro forma EPS_X = (E + a_X) / M_X   (pro forma earnings per current share over pro forma
#         shares per current share).
#   floor = required pro forma EPS; option X qualifies iff EPS_X >= floor (at least -> non-strict),
#         evaluated EXACTLY (no rounding of any intermediate value).
#   Decision: among qualifying options pick the higher exact EPS; exact tie -> option_a;
#         none qualify -> neither_option.
#
# Checkpoint a_one_stage_share_multiple_checkpoint: Option A share-base multiple after ONE stage
#   = 1 + r_A (a plain ratio/multiple, NOT cubed and NOT a percent). Returned unrounded; the
#   framework applies half-up rounding to 6 dp.
#
# Overrides of standard convention: none (the text defines its own cumulative multiple and a
# fictional scenario; no real-world accounting rule is applied).

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h018"


def solve(text: str, q: dict) -> dict:
    eps = grab(r"current common EPS {N}", text)
    floor = grab(r"pro forma EPS of at least {N}", text)
    add_a = grab(r"Option A adds total earnings of {N} per current share", text)
    r_a = grab(r"Option A adds.*?per-stage share-base increase is {N}", text)
    add_b = grab(r"Option B analogously adds {N} per current share", text)
    r_b = grab(r"Option B analogously adds.*?uses per-stage increase {N}", text)
    stages = 3  # "exactly three sequential ... stages"; cumulative multiple is (1 + ratio)^3

    mult_a = (1 + r_a) ** stages
    mult_b = (1 + r_b) ** stages
    eps_a = (eps + add_a) / mult_a
    eps_b = (eps + add_b) / mult_b

    qa = eps_a >= floor
    qb = eps_b >= floor
    if qa and qb:
        final = "option_a" if eps_a >= eps_b else "option_b"
    elif qa:
        final = "option_a"
    elif qb:
        final = "option_b"
    else:
        final = "neither_option"

    slots = {"a_one_stage_share_multiple_checkpoint": 1 + r_a}
    return {"final": final, "slots": slots}
