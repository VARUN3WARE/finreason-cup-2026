"""h095 -- maximum noncash EBITDA add-back supported by a normalized-OCF / EBITDA screen.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h095"


def solve(text: str, q: dict) -> dict:
    # "Verified recurring EBITDA before the proposed adjustment is {N}."
    ebitda_before = grab(r"EBITDA before the proposed adjustment is {N}", text)

    # "Reported operating cash flow is {N}, including a temporary working-capital release of {N}
    #  and a one-time tax refund of {N} that the reviewer removes."
    reported_ocf = grab(r"Reported operating cash flow is {N}", text)
    wc_release = grab(r"temporary working-capital release of {N}", text)
    tax_refund = grab(r"one-time tax refund of {N}", text)

    # Checkpoint 1: remove the temporary working-capital release from reported OCF.
    ocf_after_wc = reported_ocf - wc_release
    # Normalized OCF: the reviewer removes both items.
    normalized_ocf = ocf_after_wc - tax_refund

    # "The internal screen requires normalized operating cash flow divided by EBITDA after the
    #  proposed noncash management add-back of {N} to be at least {N}."
    proposed_addback = grab(r"noncash management add-back of {N}", text)
    threshold = grab(r"to be at least {N}", text)

    # "Assume the proposed add-back has no operating-cash-flow effect."
    # Screen: normalized_ocf / (ebitda_before + addback) >= threshold
    #   -> addback <= normalized_ocf / threshold - ebitda_before  (EBITDA after add-back > 0)
    max_addback = normalized_ocf / threshold - ebitda_before

    # "report the signed headroom relative to the proposed add-back"
    # positive = unused capacity, negative = proposal exceeds the screen.
    headroom = max_addback - proposed_addback

    return {
        "final": Fraction(headroom),
        "slots": {"cash_flow_after_working_capital_checkpoint": Fraction(ocf_after_wc)},
    }
