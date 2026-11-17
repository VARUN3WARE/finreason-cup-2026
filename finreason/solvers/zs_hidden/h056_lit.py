"""h056 -- two-factor modeled loss with joint interaction and concentration square;
capital charge = max(modeled loss, external stress loss).  Literal transcription."""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h056"


def solve(text: str, q: dict) -> dict:
    # "A portfolio worth {V} has factor shock ratios {s1} and {s2},"
    value = grab(r"portfolio worth {N}", text)
    s1, s2 = grab_all(r"factor shock ratios {N} and {N}", text)
    # "with respective loss sensitivities {b1} and {b2}."
    b1, b2 = grab_all(r"loss sensitivities {N} and {N}", text)
    # "Their joint effect is the product of both shocks and {c}."
    joint_coef = grab(r"product of both shocks and {N}", text)
    joint_rate = s1 * s2 * joint_coef
    # "A concentration ratio {k} adds its squared value to the modeled loss rate."
    conc = grab(r"concentration ratio {N}", text)
    conc_square = conc ** 2
    # "Compute the modeled loss from the sum of both linear factor rates, the joint rate,
    #  and the concentration square."
    linear1 = s1 * b1
    linear2 = s2 * b2
    modeled_rate = linear1 + linear2 + joint_rate + conc_square
    modeled_loss = value * modeled_rate
    # "The required capital charge is the larger of that modeled loss and external stress loss {E}."
    stress = grab(r"external stress loss {N}", text)
    capital = max(modeled_loss, stress)

    return {
        "final": Fraction(capital),
        "slots": {"joint_ratio_checkpoint": Fraction(joint_rate)},
    }
