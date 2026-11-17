"""h071 -- combined loss budget: maximum portfolio value (skeptic / ambiguity-hunting analyst).

Question shape (all 3 instances):
    "A portfolio must keep the sum of market-shock loss and liquidity-spread cost within B.
     The market shock ratio is s, its loss sensitivity is k, and the liquidity spread ratio is l.
     Both loss components scale with the same portfolio value. Compute the maximum portfolio
     value that exactly exhausts the combined loss budget."

Final  : usd, half_up 2dp      -> V
Slot   : market_ratio_checkpoint "Report the market-shock loss ratio", ratio, half_up 6dp

AMBIGUITIES CONSIDERED AND RESOLUTIONS
--------------------------------------
A1. What is the "market-shock loss"?  The text names a "market shock ratio" s and "its loss
    sensitivity" k ("its" = the market shock's).  A shock of size s with loss sensitivity k produces a
    loss of s*k per unit of portfolio value, so  market-shock loss = s*k*V.  The sensitivity multiplies
    only the market component (it is "its", the shock's, sensitivity), never the liquidity spread.
A2. What is the "liquidity-spread cost"?  "the liquidity spread ratio is l" and "Both loss components
    scale with the same portfolio value" -> liquidity-spread cost = l*V (linear in V, no sensitivity).
A3. Checkpoint "market-shock loss ratio" vs the given "market shock ratio".  The slot deliberately uses
    the hyphenated component name from sentence 1 ("market-shock loss") plus "ratio", i.e. the market
    loss expressed per unit of portfolio value = s*k, NOT the raw input s (a checkpoint that merely
    echoes an input would be described as "market shock ratio").  Unit "ratio" -> plain s*k, not percent.
    (Note: instance 3 has s = 0.0974805, which would sit on a 6dp half-up boundary if the slot were s;
    the description's wording still points to s*k, and s*k = 0.04874025 rounds cleanly.)
A4. "within B": the budget is an absolute amount in usd (final unit is usd and both components are
    losses in currency).  "exactly exhausts" -> solve the equality (s*k + l) * V = B, no inequality
    slack, no floor/ceiling, no rounding of V before reporting.
A5. "maximum portfolio value": since total loss is increasing in V (all ratios positive), the maximum
    admissible V is the one at equality: V = B / (s*k + l).
A6. Units of the inputs: all three instances give the ratios as plain decimals.  For robustness, if a
    number is immediately followed by "percent"/"%" it is divided by 100.  Budget may be prefixed by
    "USD"/"$" -- tolerated by the regex.
A7. No rounding inside the computation: nothing in the text says a rounded value is reused downstream.
    Checkpoint and final are returned as exact Fractions; the framework rounds them independently.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h071"

_PCT_RE = re.compile(r"^\s*(?:percent|per cent|pct\.?|%)", re.I)


def _num(pattern: str, text: str) -> Fraction:
    """Grab the {N} capture of ``pattern`` (first match); divide by 100 if followed by percent/%.

    Patterns are anchored on the surrounding words of the question so the instance values are never
    hardcoded.  The ``{N}`` placeholder expands to the shared NUMBER regex from finreason.nums.
    """
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"h071: pattern not found: {pattern!r}")
    value = F(m.group(1))
    if _PCT_RE.match(text[m.end(1):]):
        value /= 100
    return value


def solve(text: str, q: dict) -> dict:
    # --- parse the four inputs by anchoring on the surrounding phrases -------------------------------
    # Budget B: "... within 0.307." (optionally "within USD 9" / "within $9")
    budget = _num(r"within\s+(?:USD\s*|\$\s*)?{N}", text)
    # Market shock ratio s: "The market shock ratio is 0.2"
    shock = _num(r"market[\s-]*shock\s+ratio\s+(?:is|of|equals|=)\s*{N}", text)
    # Loss sensitivity k: "its loss sensitivity is 0.4"
    sens = _num(r"loss\s+sensitivity\s+(?:is|of|equals|=)\s*{N}", text)
    # Liquidity spread ratio l: "the liquidity spread ratio is 0.04"
    liq = _num(r"liquidity[\s-]*spread\s+ratio\s+(?:is|of|equals|=)\s*{N}", text)

    # --- computation (exact) ---------------------------------------------------------------------------
    # A1/A3: market-shock loss per unit of portfolio value = shock ratio x loss sensitivity.
    market_loss_ratio = shock * sens
    # A2: liquidity-spread cost per unit of portfolio value = liquidity spread ratio.
    combined_ratio = market_loss_ratio + liq
    if combined_ratio == 0:
        raise ValueError("h071: combined loss ratio is zero; no finite maximum portfolio value")
    # A4/A5: (s*k + l) * V = B  ->  V = B / (s*k + l), unrounded.
    portfolio_value = budget / combined_ratio

    return {
        "final": portfolio_value,
        "slots": {"market_ratio_checkpoint": market_loss_ratio},
    }
