# FINANCE MODEL (h036): merger-synergy deduplication via inclusion-exclusion.
#
#   H  = P + I + R                      unadjusted headline sum (USD m)         -> slot headline_savings_checkpoint
#   Q  = o_PI + o_PR + o_IR             sum of pairwise overlaps (each pairwise
#                                       overlap as given already INCLUDES the
#                                       common three-way overlap T)              -> slot pairwise_overlap_checkpoint
#   D  = H - Q + T                      inclusion-exclusion: subtract pairwise
#                                       overlaps, then restore the triple overlap
#                                       (it was subtracted 3x but counted 3x in
#                                       the singles, so net must be added back once)
#   Rz = ratio * D                      realized pre-tax synergy
#   NB = max(Rz, 0) - charge            annual integration charge is fully tax
#                                       deductible: deducted BEFORE tax, so the
#                                       tax base is (realized - charge)
#   NI = NB * (1 - t)                   after-tax net captured synergy
#                                       (no floor on NB: fully deductible charge
#                                       gives a symmetric tax effect; the text only
#                                       says the realized amount is "positive")
#   answer = NI / H * 100  (percent)    denominator is the UNADJUSTED headline sum
#                                       (stated "intentionally").
# Conventions/overrides: none beyond the stated denominator; numbers are USD millions, tax/ratio are decimals.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h036"


def solve(text: str, q: dict) -> dict:
    p = grab(r"procurement savings {N}", text)
    i = grab(r"IT savings {N}", text)
    r = grab(r"revenue-synergy contribution {N}", text)
    o_pi = grab(r"procurement-IT overlap {N}", text)
    o_pr = grab(r"procurement-revenue overlap {N}", text)
    o_ir = grab(r"IT-revenue overlap {N}", text)
    triple = grab(r"common three-way overlap {N}", text)
    ratio = grab(r"realize ratio {N}", text)
    charge = grab(r"annual integration charge {N}", text)
    tax = grab(r"tax rate {N}", text)

    headline = p + i + r
    pairwise = o_pi + o_pr + o_ir
    dedup = headline - pairwise + triple
    realized = ratio * dedup
    if realized < 0:
        realized = Fraction(0)
    net_pre_tax = realized - charge
    net_after_tax = net_pre_tax * (1 - tax)
    final = net_after_tax / headline * 100

    return {
        "final": final,
        "slots": {
            "headline_savings_checkpoint": headline,
            "pairwise_overlap_checkpoint": pairwise,
        },
    }
