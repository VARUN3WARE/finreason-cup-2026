"""h074 -- green/conventional tranche split: maximum total principal under a repayment cap.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab, ipow

TEMPLATE_ID = "h074"


def solve(text: str, q: dict) -> dict:
    # "The green tranche receives share S, earns annual yield ratio R, and compounds for N annual periods."
    green_share = grab(r"green tranche receives share {N}", text)
    green_yield = grab(r"green tranche receives share .*?earns annual yield ratio {N}", text)
    green_periods = grab(r"green tranche receives share .*?compounds for {N} annual periods", text)

    # "The remaining principal funds the conventional tranche, which earns annual yield ratio R
    #  and compounds for N annual periods."
    conv_share = 1 - green_share
    conv_yield = grab(r"conventional tranche, which earns annual yield ratio {N}", text)
    conv_periods = grab(
        r"conventional tranche, which earns annual yield ratio .*?compounds for {N} annual periods", text
    )

    # Compound maturity factors (annual compounding over whole periods).
    green_factor = ipow(1 + green_yield, green_periods)
    conv_factor = ipow(1 + conv_yield, conv_periods)

    # "Total maturity repayment equals the green principal share multiplied by its compound maturity
    #  factor plus the conventional principal share multiplied by its compound maturity factor."
    # Repayment per unit of total principal P:
    repayment_per_unit = green_share * green_factor + conv_share * conv_factor

    # "Given the total maturity-repayment cap C, compute the maximum total principal that makes
    #  repayment exactly equal to the cap."  ->  P * repayment_per_unit = C
    cap = grab(r"total maturity-repayment cap {N}", text)
    max_principal = Fraction(cap) / repayment_per_unit

    return {
        "final": max_principal,
        "slots": {"green_maturity_factor_checkpoint": green_factor},
    }
