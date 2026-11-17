"""h070 -- reverse a staged transfer (proportional fee, fixed fee, rebate) to a gross amount.

Literal transcription of the question:
  "A transfer is charged a proportional fee ratio of p and then a fixed network fee of c USD,
   after which a rebate of b USD is credited."
     forward chain: gross -> gross * (1 - p) -> minus c -> plus b = recipient amount
  "Determine the exact gross transfer amount required for the recipient to obtain exactly T USD."
  "Reverse the stages in order by removing the rebate, restoring the fixed fee, and dividing by
   the proportional-fee retention ratio."
     pre_rebate = T - b          (receipt required before applying the rebate -> checkpoint)
     pre_fixed  = pre_rebate + c
     gross      = pre_fixed / (1 - p)
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h070"


def _fee_ratio(text: str) -> Fraction:
    try:
        return grab(r"proportional fee ratio of {N}(?!\s*(?:percent|%))", text)
    except ValueError:
        return grab(r"proportional fee (?:ratio |rate )?of {N}\s*(?:percent|%)", text) / 100


def solve(text: str, q: dict) -> dict:
    # Sentence 1: the forward stages.
    proportional_fee_ratio = _fee_ratio(text)
    fixed_network_fee = grab(r"fixed network fee of {N}\s*USD", text)
    rebate = grab(r"rebate of {N}\s*USD", text)

    # Sentence 2: the recipient target.
    target_receipt = grab(r"recipient to obtain exactly {N}\s*USD", text)

    # Sentence 3: reverse the stages in order.
    # (a) remove the rebate -> receipt required before applying the rebate
    pre_rebate_receipt = target_receipt - rebate
    # (b) restore the fixed fee
    pre_fixed_fee_amount = pre_rebate_receipt + fixed_network_fee
    # (c) divide by the proportional-fee retention ratio
    retention_ratio = 1 - proportional_fee_ratio
    gross_transfer = pre_fixed_fee_amount / retention_ratio

    # Sanity: forward chain reproduces the target exactly.
    assert gross_transfer * retention_ratio - fixed_network_fee + rebate == target_receipt

    return {
        "final": gross_transfer,
        "slots": {"pre_rebate_checkpoint": pre_rebate_receipt},
    }
