# FINANCE MODEL (h095): quality-of-earnings cash-conversion screen with an EBITDA add-back.
#
# Inputs (USD million):
#   E      = verified recurring EBITDA before the proposed adjustment
#   OCF    = reported operating cash flow
#   WC     = temporary working-capital release embedded in OCF (non-recurring -> removed)
#   TR     = one-time tax refund embedded in OCF (non-recurring -> removed)
#   A_prop = proposed noncash management add-back (added to EBITDA; no OCF effect)
#   r      = minimum cash-conversion ratio (normalized OCF / adjusted EBITDA >= r)
#
# Normalization:
#   Checkpoint 1 (cash_flow_after_working_capital_checkpoint) = OCF - WC
#       (only the working-capital release is removed at this step; the tax refund is removed next)
#   Normalized OCF = OCF - WC - TR      (both temporary items removed by the reviewer)
#
# Screen:  Normalized OCF / (E + A) >= r   with A = add-back, no effect on OCF.
#   Since E + A > 0 and r > 0, this is equivalent to  E + A <= NormOCF / r,
#   so the maximum supported add-back is  A_max = NormOCF / r - E.
#
# Headroom (final answer) = A_max - A_prop  (signed):
#   positive -> unused screening capacity; negative -> the proposal exceeds the screen.
#
# Conventions / overrides: none beyond the text. Everything exact (Fractions), nothing rounded
# inside the computation; the framework rounds the final to 2 dp half-up and the checkpoint to 4 dp.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h095"


def solve(text: str, q: dict) -> dict:
    E = grab(r"EBITDA before the proposed adjustment is {N}", text)
    ocf = grab(r"Reported operating cash flow is {N}", text)
    wc = grab(r"working-capital release of {N}", text)
    tr = grab(r"tax refund of {N}", text)
    a_prop = grab(r"management add-back of {N}", text)
    r = grab(r"to be at least {N}", text)

    after_wc = ocf - wc
    norm_ocf = ocf - wc - tr
    a_max = norm_ocf / r - E
    headroom = a_max - a_prop

    return {
        "final": headroom,
        "slots": {"cash_flow_after_working_capital_checkpoint": after_wc},
    }
