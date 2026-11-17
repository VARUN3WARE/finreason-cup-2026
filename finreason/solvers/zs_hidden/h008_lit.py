"""h008 -- straight-line depreciation: residual value implied by a target carrying amount.

Literal transcription of the question:
  S1 "An asset has original cost C in USD millions."               -> cost = C
  S2 "Under straight-line depreciation, f of its depreciable life
      has elapsed."                                                 -> elapsed = f
       straight-line: accumulated depreciation = elapsed * (cost - residual)
  S3 "Determine the residual value that would produce a target
      carrying amount of B at that point."                          -> carrying = B
       carrying amount = cost - accumulated depreciation
       => accumulated depreciation = cost - carrying   (checkpoint 1)
       => residual = cost - accumulated depreciation / elapsed (final)
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h008"


def solve(text: str, q: dict) -> dict:
    # S1: original cost (USD millions)
    cost = grab(r"original cost (?:of )?(?:USD )?\$?{N}", text)

    # S2: fraction of depreciable life elapsed (accept a percent phrasing too)
    try:
        elapsed = grab(r"{N} percent of (?:its|the) depreciable life", text) / 100
    except ValueError:
        elapsed = grab(r"{N} of (?:its|the) depreciable life", text)
    if elapsed <= 0:
        raise ValueError("elapsed fraction of life must be positive")

    # S3: target carrying amount at that point
    carrying = grab(r"target carrying amount (?:of )?(?:USD )?\$?{N}", text)

    # Carrying amount = cost - accumulated depreciation
    accumulated_depreciation = cost - carrying

    # Straight-line: accumulated depreciation = elapsed * (cost - residual)
    depreciable_base = accumulated_depreciation / elapsed
    residual = cost - depreciable_base

    return {
        "final": Fraction(residual),
        "slots": {"implied_depreciation_checkpoint": Fraction(accumulated_depreciation)},
    }
