"""h071 -- literal transcription: max portfolio value exhausting a combined loss budget.

Sentence by sentence:
  1. "keep the sum of market-shock loss and liquidity-spread cost within B"   -> budget B
  2. "market shock ratio is s, its loss sensitivity is k,
      and the liquidity spread ratio is l"                                     -> s, k, l
  3. "Both loss components scale with the same portfolio value"               ->
         market-shock loss   = V * (s * k)      (market-shock loss ratio = s * k)
         liquidity cost      = V * l
  4. "maximum portfolio value that exactly exhausts the combined loss budget" ->
         V * (s*k + l) = B   =>   V = B / (s*k + l)
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h071"


def solve(text: str, q: dict) -> dict:
    # Sentence 1: budget on the sum of the two loss components.
    budget = grab(r"liquidity-spread cost within {N}", text)
    # Sentence 2: ratios.
    shock_ratio = grab(r"market shock ratio is {N}", text)
    loss_sensitivity = grab(r"loss sensitivity is {N}", text)
    liquidity_spread_ratio = grab(r"liquidity spread ratio is {N}", text)
    # Sentence 3: per-unit-of-portfolio-value loss components.
    market_loss_ratio = shock_ratio * loss_sensitivity
    combined_loss_ratio = market_loss_ratio + liquidity_spread_ratio
    # Sentence 4: value that exactly exhausts the budget.
    max_value = Fraction(budget) / combined_loss_ratio
    return {
        "final": max_value,
        "slots": {"market_ratio_checkpoint": market_loss_ratio},
    }
