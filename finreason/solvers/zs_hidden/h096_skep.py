"""h096 -- minimum total capital to fund a buffered high-risk allocation plus a reserve.

Text pattern:
  "A firm must support a high-risk allocation of X. Before applying its risk-appetite
   ratio r, it increases the allocation target by diversification buffer ratio b.
   It also keeps R outside the allocable capital pool. Compute the minimum total
   capital required to fund the buffered high-risk allocation and the reserve."

AMBIGUITIES AND RESOLUTIONS
1. "increases the allocation target by diversification buffer ratio b"
   - additive (+b USD)?  No: b is a *ratio* (dimensionless), so it scales the target.
   - gross-up X/(1-b)?   No: "increases by ratio b" is a proportional mark-up, so
     buffered = X * (1 + b).  (The alternative wording would be "so that the buffer
     is b of the buffered target".)
2. Risk-appetite ratio r: multiply or divide?
   - r is the share of the allocable capital pool that may sit in high-risk assets,
     i.e. r * pool >= buffered target.  The "minimum total capital required to FUND"
     the allocation is therefore pool = buffered / r.  Multiplying (buffered * r)
     would give less capital than the allocation itself, which cannot "fund" it.
3. Reserve R "kept outside the allocable capital pool":
   - not part of the pool, so it is neither divided by r nor increased by b; it is
     added once, unscaled, to the total.
4. Order of operations: the buffer is applied BEFORE the risk-appetite ratio.  Both
   are multiplicative so the final value is X*(1+b)/r + R either way, but the
   checkpoint "buffered high-risk allocation target" is specifically the quantity
   after the buffer and before the risk-appetite division: X*(1+b).
5. "minimum": the binding constraint r * pool >= buffered holds with equality; no
   whole-unit / ceiling rounding is mentioned, so no intermediate rounding is done.
   All values are returned unrounded; the framework rounds half-up to 2 dp.
6. Units: every number in the text is already in USD or a plain ratio (no "percent"),
   so no /100 conversions are needed.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h096"


def solve(text: str, q: dict) -> dict:
    # Required high-risk allocation (USD), before the diversification buffer.
    alloc = grab(r"high-risk allocation of(?: USD)? {N}", text)
    # Risk-appetite ratio: share of the allocable pool that may be high-risk.
    appetite = grab(r"risk-appetite ratio(?: of)? {N}", text)
    # Diversification buffer ratio: proportional increase of the allocation target.
    buffer = grab(r"diversification buffer ratio(?: of)? {N}", text)
    # Reserve kept outside the allocable capital pool (USD).
    reserve = grab(r"keeps(?: USD)? {N} outside the allocable capital pool", text)

    # Step 1: buffered target = X * (1 + b)   [checkpoint]
    buffered = alloc * (1 + buffer)

    # Step 2: allocable pool large enough that appetite * pool = buffered target.
    pool = buffered / appetite

    # Step 3: total capital = allocable pool + reserve held outside the pool.
    total = pool + reserve

    return {
        "final": Fraction(total),
        "slots": {"buffered_target_checkpoint": Fraction(buffered)},
    }
