"""Hidden cluster h009 -- two-network transfer routing with a threshold rule.

Structure (identical across the 3 instances; only the numbers differ):
    A transfer of P USD may use Network A or Network B.
    Network A deducts fee ratio rA and then fixed fee fA USD.
    Network B deducts fee ratio rB, then fixed fee fB USD, and finally increases
    the post-fee amount by bonus ratio b.
    Use Network A if its (unrounded) net receipt is at least T USD (equality
    included); otherwise use Network B.  Report the selected net receipt (USD).
    Checkpoint: Network B's receipt after its proportional fee and before its
    fixed fee and bonus (USD).

AMBIGUITY HUNT -- points where two analysts could disagree, and the resolution:

 1. "fee ratio X" -- ratio vs percent.  Resolved: a plain RATIO (dimensionless
    fraction of the amount).  Evidence: the word "ratio" and values such as 0.4,
    0.39998, 8999/30000 that are obviously fractions of one, not percents.
    So the proportional fee is P*r and the remainder is P*(1 - r).

 2. Which base does the proportional fee apply to?  Resolved: the gross
    transfer amount P, because the fee ratio is the FIRST deduction on each
    network ("deducts fee ratio ... and then fixed fee ...").

 3. Order of the fixed fee vs proportional fee.  Resolved: proportional first,
    then fixed, on both networks -- explicit wording "and then fixed fee" (A) and
    "then fixed fee" (B).  A_net = P*(1 - rA) - fA.

 4. Network B bonus -- what it multiplies and how.  Resolved: the bonus is a
    RATIO applied to the POST-FEE amount (after BOTH the proportional and the
    fixed fee), i.e. B_net = (P*(1 - rB) - fB) * (1 + b).  Evidence: "finally
    increases the post-fee amount by bonus ratio b" -- "finally" places it last,
    "post-fee amount" names the base, "increases ... by ratio" means multiply by
    (1 + b), not add b USD and not fold it into the fee ratio as (1 - rB + b).

 5. Threshold comparison.  Resolved: NON-STRICT, A_net >= T -> use A, else B.
    Evidence: "at least T USD, including exact equality".  The comparison uses
    the UNROUNDED A_net ("Using unrounded intermediate amounts"); no rounding
    happens before the test.

 6. Which quantity the final answer is.  Resolved: the net receipt of the
    SELECTED network (A_net if A chosen, else B_net), in USD, unrounded here;
    the framework rounds half-up to 2 dp.  Both candidates are computed first
    ("Compute both candidate route receipts before applying the routing rule")
    but only the selected one is reported.

 7. Checkpoint quantity.  Resolved: P*(1 - rB) -- Network B's amount remaining
    after its proportional fee and BEFORE its fixed fee and bonus, in USD.
    Not the fee itself (P*rB), not the post-fixed-fee amount, not the bonus
    amount.  Evidence: slot description "receipt after its proportional fee and
    before its fixed fee and bonus".

 8. Floors / sign handling.  No floor at zero or any clamp is stated, so none is
    applied: receipts are carried as exact (possibly negative) rationals.

 9. Rounding inside the chain.  The text says to carry all arithmetic exactly
    and round only the selected receipt, so every value returned here is the
    exact unrounded Fraction.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h009"


def solve(text: str, q: dict) -> dict:
    # Gross transfer amount (USD).
    principal = grab(r"transfer of\s+{N}\s+USD", text)

    # Network A: proportional fee ratio, then fixed fee (USD).
    fee_ratio_a = grab(r"Network A deducts fee ratio\s+{N}", text)
    fixed_fee_a = grab(r"Network A deducts fee ratio\s+(?:{N})\s+and then fixed fee\s+{N}\s+USD", text, group=2)

    # Network B: proportional fee ratio, then fixed fee (USD), then bonus ratio.
    fee_ratio_b = grab(r"Network B deducts fee ratio\s+{N}", text)
    fixed_fee_b = grab(r"Network B deducts fee ratio\s+(?:{N}),\s+then fixed fee\s+{N}\s+USD", text, group=2)
    bonus_ratio_b = grab(r"increases the post-fee amount by bonus ratio\s+{N}", text)

    # Routing threshold (USD) for Network A's net receipt.
    threshold = grab(r"at least\s+{N}\s+USD", text)

    one = Fraction(1)

    # Network A: proportional fee first, then fixed fee.
    net_a = principal * (one - fee_ratio_a) - fixed_fee_a

    # Network B: proportional fee -> fixed fee -> bonus on the post-fee amount.
    b_after_ratio_fee = principal * (one - fee_ratio_b)          # checkpoint
    b_post_fee = b_after_ratio_fee - fixed_fee_b
    net_b = b_post_fee * (one + bonus_ratio_b)

    # Routing rule: A if its unrounded net receipt is at least the threshold
    # (equality included), otherwise B.
    selected = net_a if net_a >= threshold else net_b

    return {
        "final": selected,
        "slots": {
            "network_b_after_ratio_fee_checkpoint": b_after_ratio_fee,
        },
    }
