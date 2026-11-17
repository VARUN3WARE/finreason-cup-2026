"""h050 -- two-plan transfer pricing comparison over a monthly horizon (skeptic / ambiguity-hunting analyst).

Structure (all 3 instances):
  A customer expects monthly transfer volume V and n transfers per month for M months.
  Plan A charges proportional transfer rate rA, fee fA per transfer, monthly subscription sA,
  and one-time setup fee SA.  Plan B charges rB, fB, sB, and one-time setup fee SB (same order).
  Each setup fee is charged exactly once.  Savings = Plan B total cost - Plan A total cost (signed).

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
1. "proportional transfer rate 0.01": ratio or percent?
   -> RATIO.  No "percent"/"%" anywhere; values 0.01..0.03 are stated bare.  Cost = rate * volume.
2. What base does the proportional rate apply to: monthly volume, total volume, or per-transfer amount?
   -> Total horizon volume (= V * M).  Applying it per month and summing gives the identical number,
      so there is no real fork here.  "proportional" = proportional to money moved, not to count.
3. Per-transfer fee base: count of transfers over the horizon (= n * M), NOT the volume.
   "fee 2 per transfer" is unambiguous.
4. Monthly subscription: charged once per month for M months -> s * M.
5. Setup fee: text says explicitly "charged exactly once at account opening, not once per month or
   transfer" -> added once, un-multiplied.
6. Plan B's bare list "charges 0.02, 1, 14, and one-time setup fee 76": same order as Plan A's labelled
   list (rate, per-transfer fee, subscription, setup).  The explicit label on the last item ("one-time
   setup fee") confirms the positional correspondence.  Parsed positionally, cross-checked against the
   labelled form when labels are present (Plan A).
7. Sign of the final answer: "Plan A savings relative to Plan B, defined as Plan B total cost minus
   Plan A total cost" -> final = cost_B - cost_A, SIGNED (negative allowed, as in instance 1).
   The minuend/subtrahend are parsed from the "defined as Plan X total cost minus Plan Y total cost"
   clause rather than assumed, so a swapped definition in another instance is still honoured.
8. Checkpoint 1 "total transfer volume over the horizon" (usd, 4 dp): V * M, i.e. the HORIZON total,
   not the monthly figure.  Checkpoint 2 "total transfer count over the horizon" (dimensionless, 0 dp):
   n * M.  Both are plain products; no rounding happens inside the chain.
9. Rounding: "Using full precision" and "round only the final value half up" -> everything is exact
   Fraction; the framework rounds.  Instance 2's savings is exactly 86.015 (a true half-up tie), so
   exact arithmetic genuinely matters here.
10. Horizon unit: "for 8 months" with "monthly" volume/count/subscription -> months everywhere, no
    annualisation anywhere.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab, numbers

TEMPLATE_ID = "h050"

_PLAN_SEG = re.compile(r"Plan\s+([A-Z])\s+charges\s*(.*?)\.(?=\s|$)", re.S)


def _plan_params(label: str, seg: str) -> dict[str, Fraction]:
    """Return {rate, fee, sub, setup} for one plan segment.

    Positional parse (the four numbers in reading order) is the primary route because Plan B is stated
    as a bare list.  When the labels are present (Plan A) the labelled grabs must agree with the
    positional ones; a disagreement raises rather than silently picking one.
    """
    nums = numbers(seg)
    if len(nums) != 4:
        raise ValueError(f"Plan {label}: expected 4 charge numbers, found {len(nums)}: {nums}")
    rate, fee, sub, setup = nums

    labelled: dict[str, Fraction] = {}
    for key, pat in (
        ("rate", r"rate\s+{N}"),
        ("fee", r"fee\s+{N}\s+per\s+transfer"),
        ("sub", r"subscription\s+{N}"),
        ("setup", r"setup\s+fee\s+{N}"),
    ):
        if re.search(pat.replace("{N}", f"({NUMBER})"), seg, flags=re.S):
            labelled[key] = grab(pat, seg)
    positional = {"rate": rate, "fee": fee, "sub": sub, "setup": setup}
    for key, val in labelled.items():
        if val != positional[key]:
            raise ValueError(f"Plan {label}: labelled {key}={val} disagrees with positional {positional[key]}")
    return positional


def solve(text: str, q: dict) -> dict:
    # --- customer usage profile ----------------------------------------------------------------
    monthly_volume = grab(r"monthly\s+transfer\s+volume\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    monthly_count = grab(r"{N}\s+transfers\s+per\s+month", text)
    months = grab(r"for\s+{N}\s+months?", text)

    horizon_volume = monthly_volume * months   # checkpoint 1 (usd)
    horizon_count = monthly_count * months     # checkpoint 2 (dimensionless)

    # --- plan tariffs ----------------------------------------------------------------------------
    plans: dict[str, dict[str, Fraction]] = {}
    for m in _PLAN_SEG.finditer(text):
        plans[m.group(1)] = _plan_params(m.group(1), m.group(2))
    if len(plans) < 2:
        raise ValueError(f"expected two plans, parsed {sorted(plans)}")

    def total_cost(p: dict[str, Fraction]) -> Fraction:
        return (
            p["rate"] * horizon_volume      # proportional charge on money moved
            + p["fee"] * horizon_count      # per-transfer fee on number of transfers
            + p["sub"] * months             # monthly subscription, once per month
            + p["setup"]                    # one-time setup fee, charged exactly once
        )

    costs = {label: total_cost(p) for label, p in plans.items()}

    # --- savings definition: "defined as Plan X total cost minus Plan Y total cost" ---------------
    m = re.search(r"defined\s+as\s+Plan\s+([A-Z])\s+total\s+cost\s+minus\s+Plan\s+([A-Z])\s+total\s+cost", text)
    if m is None:
        # Fallback to the stated semantics: Plan A savings relative to Plan B = cost_B - cost_A.
        minuend, subtrahend = "B", "A"
    else:
        minuend, subtrahend = m.group(1), m.group(2)
    savings = costs[minuend] - costs[subtrahend]

    return {
        "final": savings,
        "slots": {
            "horizon_volume_checkpoint": horizon_volume,
            "horizon_count_checkpoint": horizon_count,
        },
    }
