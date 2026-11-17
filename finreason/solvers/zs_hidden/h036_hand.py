from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h036"


def solve(text: str, q: dict) -> dict:
    proc = grab(r"procurement savings {N}", text)
    it = grab(r"IT savings {N}", text)
    rev = grab(r"revenue-synergy contribution {N}", text)
    o_pi = grab(r"procurement-IT overlap {N}", text)
    o_pr = grab(r"procurement-revenue overlap {N}", text)
    o_ir = grab(r"IT-revenue overlap {N}", text)
    triple = grab(r"common three-way overlap {N}", text)
    realize = grab(r"realize ratio {N}", text)
    charge = grab(r"integration charge {N}", text)
    tax = grab(r"tax rate {N}", text)

    headline = proc + it + rev
    pairwise = o_pi + o_pr + o_ir
    dedup = headline - pairwise + triple
    realized = realize * dedup
    # "positive realized amount": realized value floored at zero
    realized = max(realized, Fraction(0))
    pre_tax = realized - charge
    after_tax = pre_tax * (1 - tax)
    final = after_tax / headline * 100

    return {
        "final": final,
        "slots": {
            "headline_savings_checkpoint": headline,
            "pairwise_overlap_checkpoint": pairwise,
        },
    }
