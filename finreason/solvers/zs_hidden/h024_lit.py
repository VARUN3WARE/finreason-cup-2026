"""h024 -- maximum preferred-dividend allocation per current common share that keeps
pro forma post-issuance EPS at or above a floor (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h024"


def solve(text: str, q: dict) -> dict:
    # "earnings normalized per current common share are E" (before preferred distributions and issuance)
    e_per_current = grab(r"earnings normalized per current common share are {N}", text)
    # "The issuance increases the common-share base by ratio g"
    g = grab(r"increases the common-share base by ratio {N}", text)
    # "keep exact pro forma post-issuance EPS at or above T"
    eps_floor = grab(r"post-issuance EPS at or above {N}", text)

    # Post-issuance share base, as a multiple of the current share base.
    multiple = Fraction(1) + g

    # Pro forma EPS = (E - P) / multiple >= T  (all per current common share, P = preferred allocation)
    # => P <= E - T * multiple ; the maximum allocation is the binding value ("at or above" -> equality allowed).
    p_max = e_per_current - eps_floor * multiple

    return {"final": p_max, "slots": {"dilution_multiple_checkpoint": multiple}}
