from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h095"


def solve(text: str, q: dict) -> dict:
    ebitda = grab(r"recurring EBITDA before the proposed adjustment is {N}", text)
    ocf = grab(r"Reported operating cash flow is {N}", text)
    wc = grab(r"temporary working-capital release of {N}", text)
    tax = grab(r"one-time tax refund of {N}", text)
    addback = grab(r"proposed noncash management add-back of {N}", text)
    threshold = grab(r"to be at least {N}", text)

    # Checkpoint 1: reported OCF less the temporary working-capital release
    cf_after_wc = ocf - wc
    # Normalized OCF: also remove the one-time tax refund
    norm_ocf = cf_after_wc - tax

    # Screen: norm_ocf / (ebitda + A) >= threshold  ->  A <= norm_ocf / threshold - ebitda
    max_addback = norm_ocf / threshold - ebitda
    headroom = max_addback - addback

    return {
        "final": Fraction(headroom),
        "slots": {"cash_flow_after_working_capital_checkpoint": Fraction(cf_after_wc)},
    }
