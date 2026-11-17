"""Solver for hidden cluster h036 -- merger-synergy inclusion-exclusion, realization, integration charge, tax.

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED (all from the question text):

1. Inclusion-exclusion form.  The text says "Each pairwise overlap includes the same common
   three-way overlap", i.e. the pairwise numbers are FULL intersections |A&B|, |A&C|, |B&C|
   (not triple-exclusive regions).  So the standard formula applies:
       dedup = (P + I + R) - (PI + PR + IR) + T
   (add T back ONCE; the "subtract 2T" variant would only apply if the pairwise overlaps
   excluded the triple region, which the text rules out).

2. Checkpoint 1 "headline_savings_checkpoint" = unadjusted headline SUM = P + I + R
   (usd_million).  This is also the denominator the question says to use "intentionally".

3. Checkpoint 2 "pairwise_overlap_checkpoint" = the RAW sum of the three pairwise overlaps
   PI + PR + IR "before restoring the common three-way overlap" -- NOT the net deduction
   (pairs - T) and NOT the deduplicated amount.

4. "realize ratio 0.9" and "tax rate 0.2" are given as plain ratios (no "percent"), so they
   are used as-is.  Defensive: if an instance ever says "... percent", divide by 100.

5. "Deduct fully tax-deductible annual integration charge C from the positive realized
   amount before applying tax rate t": the charge is a pre-tax deduction, so
       pre_tax_net = realized - C ;  after_tax = pre_tax_net * (1 - t).
   "positive realized amount" is read as descriptive (the realized amount is positive), not
   as a floor instruction.  Checked: all three instances keep realized, pre_tax_net and
   after_tax strictly positive, so no floor/branch question is actually triggered.

6. Final answer unit is percent: after_tax / (P + I + R) * 100, returned UNROUNDED;
   the framework rounds half-up to 2 dp.  Nothing in the text asks for intermediate rounding.

7. Parsing is anchored on the surrounding words ("procurement savings", "IT savings",
   "revenue-synergy contribution", "procurement-IT overlap", "procurement-revenue overlap",
   "IT-revenue overlap", "three-way overlap", "realize ratio", "integration charge",
   "tax rate").  The word "Three" at the start is not a digit and is never captured.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h036"


def _ratio(pattern: str, text: str) -> Fraction:
    """Grab a rate; if the number is immediately followed by 'percent' / '%', convert to ratio."""
    val = grab(pattern, text)
    rx = pattern.replace("{N}", r"(-?[\d,]+(?:\.\d+)?(?:/\d+)?)")
    m = re.search(rx, text, flags=re.S)
    tail = text[m.end(): m.end() + 12] if m else ""
    if re.match(r"\s*(percent|%)", tail):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    # --- headline values (USD millions)
    proc = grab(r"procurement savings\s+{N}", text)
    it = grab(r"IT savings\s+{N}", text)
    rev = grab(r"revenue-synergy contribution\s+{N}", text)

    # --- pairwise overlaps (each INCLUDES the triple overlap)
    o_pi = grab(r"procurement-IT overlap\s+{N}", text)
    o_pr = grab(r"procurement-revenue overlap\s+{N}", text)
    o_ir = grab(r"IT-revenue overlap\s+{N}", text)

    # --- common three-way overlap
    triple = grab(r"three-way overlap\s+{N}", text)

    # --- realization ratio, integration charge, tax rate
    realize = _ratio(r"realize ratio\s+{N}", text)
    charge = grab(r"integration charge\s+{N}", text)
    tax = _ratio(r"tax rate\s+{N}", text)

    # Checkpoint 1: unadjusted headline sum
    headline_sum = proc + it + rev

    # Checkpoint 2: raw sum of pairwise overlaps (before adding the triple back)
    pairwise_sum = o_pi + o_pr + o_ir

    # Inclusion-exclusion deduplication: |A u B u C| = sum - pairs + triple
    dedup = headline_sum - pairwise_sum + triple

    # Realize the stated fraction of the deduplicated amount
    realized = realize * dedup

    # Deduct the (fully tax-deductible) integration charge pre-tax, then tax
    pre_tax_net = realized - charge
    after_tax = pre_tax_net * (1 - tax)

    # Percentage of the unadjusted headline sum (denominator intentionally the headline sum)
    final_pct = after_tax / headline_sum * 100

    return {
        "final": final_pct,
        "slots": {
            "headline_savings_checkpoint": headline_sum,
            "pairwise_overlap_checkpoint": pairwise_sum,
        },
    }
