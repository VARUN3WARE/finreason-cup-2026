"""h096 -- buffered high-risk allocation funded under a risk-appetite ratio, plus an outside reserve.

Literal transcription:
  "A firm must support a high-risk allocation of A."
  "Before applying its risk-appetite ratio p, it increases the allocation target by diversification
   buffer ratio b."                      -> buffered target T = A * (1 + b)   (checkpoint)
  Applying the risk-appetite ratio: at most p of the allocable pool may go to the high-risk allocation,
  so the minimum allocable pool that funds T is T / p.
  "It also keeps R outside the allocable capital pool." -> reserve added on top of the pool.
  "Compute the minimum total capital required to fund the buffered high-risk allocation and the
   reserve."                             -> total = T / p + R
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h096"


def solve(text: str, q: dict) -> dict:
    # Sentence 1: required high-risk allocation.
    allocation = grab(r"high-risk allocation of {N}", text)
    # Sentence 2: risk-appetite ratio and diversification buffer ratio.
    risk_appetite = grab(r"risk-appetite ratio {N}", text)
    buffer_ratio = grab(r"diversification buffer ratio {N}", text)
    # Buffer is applied to the target BEFORE the risk-appetite ratio.
    buffered_target = allocation * (1 + buffer_ratio)
    # Sentence 3: reserve held outside the allocable pool.
    reserve = grab(r"keeps {N} outside the allocable capital pool", text)
    # Risk-appetite ratio caps the high-risk share of the allocable pool -> minimum pool = target / ratio.
    allocable_pool = buffered_target / risk_appetite
    total_capital = allocable_pool + reserve
    return {
        "final": Fraction(total_capital),
        "slots": {"buffered_target_checkpoint": Fraction(buffered_target)},
    }
