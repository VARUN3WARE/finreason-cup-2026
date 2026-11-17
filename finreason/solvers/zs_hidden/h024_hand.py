from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h024"


def solve(text: str, q: dict) -> dict:
    # Earnings per CURRENT common share, before preferred distributions.
    e = grab(r"earnings normalized per current common share are {N}", text)
    # Issuance increases the common-share base by this ratio -> base multiple = 1 + ratio.
    r = grab(r"increases the common-share base by ratio {N}", text)
    # EPS floor (pro forma, post-issuance).
    t = grab(r"post-issuance EPS at or above {N}", text)

    multiple = 1 + r
    # Pro forma EPS = (E - D) / multiple >= T  <=>  D <= E - T * multiple
    d_max = e - t * multiple

    return {
        "final": Fraction(d_max),
        "slots": {"dilution_multiple_checkpoint": Fraction(multiple)},
    }
