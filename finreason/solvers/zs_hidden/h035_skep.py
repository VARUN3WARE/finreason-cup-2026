"""h035 -- crypto shock with severe/mild support policy, net price after flat deduction.

Structure (all 3 instances share identical wording, different numbers / branch):
    A crypto asset starts at P USD per token and loses fraction L of its price in a
    global shock. The severe policy applies when that loss ratio is at least T;
    otherwise the mild policy applies. After the shock, the severe policy increases
    the post-shock price by support ratio s_sev and then deducts d_sev USD per token.
    The mild policy increases it by support ratio s_mild and then deducts d_mild USD.
    Report the resulting net price (USD, 2 dp half-up at the end).

Checkpoint post_shock_retention_checkpoint (ratio, 6 dp half-up):
    "the share of the initial price retained after the shock"  = post_shock / P = 1 - L.

AMBIGUITIES CONSIDERED AND RESOLUTIONS (with textual evidence):
  A1. Is L a ratio or a percent?  "loses fraction L of its price" -> plain ratio
      (values 1/3, 0.2499995, 0.2). Post-shock price = P * (1 - L). No /100.
  A2. Which quantity is compared with the threshold T?  "The severe policy applies
      when THAT LOSS RATIO is at least T" -> the loss fraction L itself (not the
      retained share 1-L, not the USD loss). Comparison is exact Fraction vs Fraction.
  A3. Strict or non-strict?  "at least" -> severe iff L >= T; "otherwise" (L < T) -> mild.
      Instance 1: L = 1/3 = 0.3333333... < T = 0.3333334 -> mild (a float/approximate
      comparison could flip this, so compare exact rationals).
  A4. Base of the support increase?  "increases the POST-SHOCK PRICE by support ratio s"
      -> multiplicative on the post-shock price: post * (1 + s). Not s of the initial
      price, not an additive USD amount. "mild policy increases IT" -> same base
      (the post-shock price).
  A5. Order of operations?  "increases ... AND THEN deducts d USD per token" -> apply
      the (1 + s) factor first, then subtract the flat USD deduction d.
  A6. Is the deduction a ratio?  "deducts d USD per token" -> flat USD amount per token,
      subtracted once. The answer is per token (initial price is also per token).
  A7. Floor at zero / sign?  Nothing in the text floors the net price at zero, so the
      net price is returned as computed (sign preserved). All 3 instances are positive.
  A8. Checkpoint definition?  "share of the initial price retained after the shock"
      = post_shock_price / initial_price = 1 - L, a dimensionless ratio in [0, 1].
      Returned UNROUNDED; the framework renders it at 6 dp half-up. (Instance 2 is an
      exact midpoint 0.7500005 -> 0.750001 with exact half-up; float would get this wrong.)
  A9. Rounding inside the chain?  "exact arithmetic and two-decimal half-up rounding only
      at the end" -> no intermediate rounding; the displayed checkpoint is never fed back.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h035"


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on surrounding words; never hardcode instance values) ---
    initial = grab(r"starts at {N} USD per token", text)
    loss = grab(r"loses fraction {N} of its price", text)
    threshold = grab(r"loss ratio is at least {N}", text)
    sev_support, sev_deduct = grab_all(
        r"severe policy increases the post-shock price by support ratio {N}"
        r" and then deducts {N} USD per token",
        text,
    )
    mild_support, mild_deduct = grab_all(
        r"mild policy increases it by support ratio {N}"
        r" and then deducts {N} USD per token",
        text,
    )

    # --- shock (A1, A8) ---
    retention = Fraction(1) - loss                 # share of initial price retained
    post_shock = initial * retention               # USD per token after the shock

    # --- policy selection (A2, A3): severe iff loss ratio >= threshold ---
    if loss >= threshold:
        support, deduct = sev_support, sev_deduct
    else:
        support, deduct = mild_support, mild_deduct

    # --- policy application (A4, A5, A6): multiply by (1 + s), then subtract flat USD ---
    supported = post_shock * (Fraction(1) + support)
    net_price = supported - deduct                 # A7: no floor, sign preserved

    return {
        "final": net_price,
        "slots": {"post_shock_retention_checkpoint": retention},
    }
