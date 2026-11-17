"""h036 -- merger-synergy deduplication (inclusion-exclusion), realization, charge, tax.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h036"


def solve(text: str, q: dict) -> dict:
    # S2: "Their unadjusted headline values are procurement savings A, IT savings B,
    #      and revenue-synergy contribution C, all in USD millions."
    procurement = grab(r"procurement savings {N}", text)
    it = grab(r"IT savings {N}", text)
    revenue = grab(r"revenue-synergy contribution {N}", text)

    # S3: "Due diligence identifies procurement-IT overlap X, procurement-revenue overlap Y,
    #      and IT-revenue overlap Z."
    ov_pi = grab(r"procurement-IT overlap {N}", text)
    ov_pr = grab(r"procurement-revenue overlap {N}", text)
    ov_ir = grab(r"IT-revenue overlap {N}", text)

    # S4: "Each pairwise overlap includes the same common three-way overlap T."
    triple = grab(r"common three-way overlap {N}", text)

    # Checkpoint 1: unadjusted headline sum across the three workstreams.
    headline_sum = procurement + it + revenue

    # Checkpoint 2: sum of pairwise overlaps before restoring the three-way overlap.
    pairwise_sum = ov_pi + ov_pr + ov_ir

    # S5: "Apply inclusion-exclusion to deduplicate the headline opportunities,
    #      then realize ratio r of that deduplicated amount."
    deduplicated = headline_sum - pairwise_sum + triple
    realize_ratio = grab(r"realize ratio {N}", text)
    realized = realize_ratio * deduplicated

    # S6: "Deduct fully tax-deductible annual integration charge K from the positive
    #      realized amount before applying tax rate t."
    charge = grab(r"integration charge {N}", text)
    tax_rate = grab(r"tax rate {N}", text)
    positive_realized = max(realized, Fraction(0))
    pre_tax_net = positive_realized - charge
    # Charge is fully tax-deductible: tax applies to the net-of-charge amount
    # (sign preserved -- a net loss would carry the corresponding tax shield).
    after_tax_net = pre_tax_net * (1 - tax_rate)

    # S7/S8: percentage of the unadjusted headline sum (denominator = sum of headline values).
    final_pct = after_tax_net / headline_sum * 100

    return {
        "final": final_pct,
        "slots": {
            "headline_savings_checkpoint": headline_sum,
            "pairwise_overlap_checkpoint": pairwise_sum,
        },
    }
