"""Hidden cluster h001 -- current ratio with cash-funded purchase, then maximum
extra short-term borrowing added to BOTH current assets and current liabilities
so that the required current ratio is met exactly.

AMBIGUITY HUNT (resolved before coding):

1. "The required current ratio is one plus the ratio 0.4"
   -> r = 1 + 0.4 = 1.4 (a plain multiple, not 0.4, not 1.04, not a percent).
   Evidence: dev gold for a seen template using the identical phrasing
   ("Growth factor equals one plus the ratio", ratio 0.1) gives growth_factor 1.1.

2. "cash-funded non-current-asset purchase of P, which reduces current assets by
   the purchase amount" -> only current assets fall: CA' = CA - P. Current
   liabilities are unchanged by the purchase (it is paid in cash, no new debt).

3. Checkpoint post_purchase_assets_checkpoint = "current assets remaining after
   the planned non-current-asset purchase" = CA - P, in USD millions, BEFORE any
   borrowing is added (position 1 in the chain; text orders purchase first).

4. "additional short-term borrowing that can be added to both cash and current
   liabilities" -> borrowing B raises the numerator (cash is a current asset)
   and the denominator by the same amount: (CA' + B) / (CL + B).

5. "while exactly meeting the required current ratio" -> equality, not >=.
   Solve (CA' + B) / (CL + B) = r  =>  B = (CA' - r*CL) / (r - 1).
   "maximum" is consistent with the equality point: for r > 1 the ratio is
   strictly decreasing in B, so the largest admissible B is where it equals r.

6. No floor at zero is stated, so the sign is preserved (a negative result would
   mean no positive borrowing can satisfy the constraint). All three instances
   yield positive borrowing, so this branch is moot here.

7. Units: every input is "in USD millions"; the final answer and the checkpoint
   are both usd_million, so values pass through with no scaling.

8. Rounding: nothing says a rounded intermediate is re-used, so no rounding
   happens inside the computation. Exactness matters: instance 1 gives exactly
   63.125 (half case -> 63.13) and instance 2's checkpoint is exactly 120.315
   (half case -> 120.32). Fractions throughout; the liabilities are rationals
   like 1975/28 which the number regex parses exactly.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h001"


def _required_ratio(text: str) -> Fraction:
    # Primary phrasing: "required current ratio is one plus the ratio 0.4"
    try:
        return 1 + grab(r"required current ratio is one plus (?:the ratio )?{N}", text)
    except ValueError:
        pass
    try:
        return 1 + grab(r"one plus the ratio {N}", text)
    except ValueError:
        pass
    # Fallback: ratio stated directly ("required current ratio is 1.4").
    return grab(r"required current ratio is {N}", text)


def solve(text: str, q: dict) -> dict:
    ca = grab(r"current assets of {N}", text)
    cl = grab(r"current liabilities of {N}", text)
    purchase = grab(r"purchase of {N}", text)
    r = _required_ratio(text)

    # Step 1: cash-funded purchase reduces current assets only.
    post_purchase_assets = ca - purchase

    # Step 2: borrowing B added to both current assets and current liabilities,
    # ratio met exactly: (CA' + B) / (CL + B) = r  =>  B = (CA' - r*CL) / (r - 1).
    if r == 1:
        raise ValueError("required current ratio of exactly 1 has no unique borrowing solution")
    borrowing = (post_purchase_assets - r * cl) / (r - 1)

    return {
        "final": borrowing,
        "slots": {"post_purchase_assets_checkpoint": post_purchase_assets},
    }
