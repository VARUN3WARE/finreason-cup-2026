"""Cluster h029 -- rolling whale threshold: required next transfer to exceed the
risk-adjusted threshold by an exact margin.

Structure (all 3 instances):
    "A wallet has two prior transfers of A USD and B USD in the current monitoring
    window. Its base rolling whale threshold is T USD and is increased by
    risk-adjustment ratio r. What next transfer amount would make the rolling total
    exceed the adjusted threshold by exactly E USD?"

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
1. How the ratio r adjusts the threshold.
   Candidates: T*(1+r) / T*r / T+r.
   Resolution: T*(1+r). "increased by risk-adjustment ratio r" is a proportional
   increase (r is dimensionless, called a "ratio"). T*r with r<1 would be a
   DEcrease, contradicting "increased"; T+r adds a dimensionless number to a USD
   amount (unit mismatch, ~0.3 USD on a ~900 USD threshold).

2. What the checkpoint "multiplicative risk-adjustment factor used by the rolling
   whale threshold" denotes.  Candidates: 1+r or r.
   Resolution: 1+r. The text names r a "ratio"; the slot asks for the
   "multiplicative ... factor", i.e. the number the base threshold is multiplied
   by, with unit "multiple" (e.g. 1.3074703). Returned exact; framework rounds to
   6 dp half-up.

3. "exceed the adjusted threshold by exactly E" -> strict equality:
   (A + B + x) = T*(1+r) + E  ->  x = T*(1+r) + E - (A + B).
   Not an inequality / "at least"; "exactly" pins the margin.

4. Rolling total = all transfers in the current window, i.e. the prior transfers
   plus the next transfer (the one asked for).

5. Sign / floor at zero: the text states no floor, no "if already exceeded"
   branch. In one instance the prior transfers already exceed T*(1+r)+E, so the
   algebraic x is negative; it is returned as-is (apply only the rules stated).

6. Rounding: the final USD value is rounded half-up to 2 dp by the framework
   only; nothing in the text says a rounded value feeds anything downstream, so
   everything stays exact Fractions.

7. Direction wording: all instances say "increased by"; for robustness a
   "decreased/reduced/lowered by" variant maps to factor 1-r.

8. Number of prior transfers: the text says "two"; parsing collects every USD
   amount between "prior transfers of" and "in the current monitoring window",
   so it does not depend on the count.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, numbers

TEMPLATE_ID = "h029"


def _prior_transfers(text: str) -> list[Fraction]:
    m = re.search(
        r"prior transfers?\s+of\s+(.*?)\s+in the current monitoring window",
        text,
        flags=re.S,
    )
    if m is None:
        # Fallback: amounts listed as "<N> USD" before the threshold sentence.
        head = text.split("base rolling whale threshold")[0]
        return numbers(head.split("transfers")[-1])
    return numbers(m.group(1))


def _adjust_direction(text: str) -> int:
    """+1 if the threshold is increased by the ratio, -1 if decreased."""
    m = re.search(
        r"(increased|raised|scaled up|decreased|reduced|lowered|scaled down)\s+by\s+(?:the\s+)?risk-adjustment ratio",
        text,
        flags=re.I,
    )
    if m is None:
        return 1
    word = m.group(1).lower()
    return -1 if word in ("decreased", "reduced", "lowered", "scaled down") else 1


def solve(text: str, q: dict) -> dict:
    prior = _prior_transfers(text)
    prior_sum = sum(prior, Fraction(0))

    base_threshold = grab(r"base rolling whale threshold is {N} USD", text)
    ratio = grab(r"risk-adjustment ratio\s+(?:of\s+)?{N}", text)
    direction = _adjust_direction(text)

    # Checkpoint: multiplicative factor applied to the base threshold.
    factor = Fraction(1) + direction * ratio
    adjusted_threshold = base_threshold * factor

    excess = grab(r"exceed the adjusted threshold by exactly {N} USD", text)

    # prior_sum + x = adjusted_threshold + excess
    required_transfer = adjusted_threshold + excess - prior_sum

    return {
        "final": required_transfer,
        "slots": {"threshold_adjustment_factor_checkpoint": factor},
    }
