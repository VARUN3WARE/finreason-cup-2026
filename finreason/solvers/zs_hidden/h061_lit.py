"""h061 -- revenue required to hit a target after-tax income (literal transcription).

Sentence 1: variable COGS rate v (ratio of revenue), fixed operating costs FC, interest expense INT,
            income tax rate t (ratio).
Sentence 2: required revenue R such that after-tax income = target NI.
            NI = (R - v*R - FC - INT) * (1 - t)
            => pre-tax income needed = NI / (1 - t)   (retention ratio = 1 - t)
            => R = (NI / (1 - t) + FC + INT) / (1 - v)
Sentence 3: result in USD millions (inputs are already in the same units).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h061"


def solve(text: str, q: dict) -> dict:
    # Sentence 1
    v = grab(r"variable COGS rate(?: ratio)? of {N}", text)
    fc = grab(r"fixed operating costs of {N}", text)
    interest = grab(r"interest expense of {N}", text)
    t = grab(r"income tax rate(?: ratio)? of {N}", text)
    # tolerate percent wording if present
    if "income tax rate ratio" not in text and t > 1:
        t = t / 100
    if "COGS rate ratio" not in text and v > 1:
        v = v / 100

    # Sentence 2
    ni_target = grab(r"after-tax income of {N}", text)

    retention = Fraction(1) - t                 # after-tax retention ratio
    ebt_required = ni_target / retention        # pre-tax income needed
    ebit_required = ebt_required + interest     # operating income needed
    contribution_required = ebit_required + fc  # contribution margin needed
    revenue = contribution_required / (Fraction(1) - v)

    return {"final": revenue, "slots": {"retention_ratio_checkpoint": retention}}
