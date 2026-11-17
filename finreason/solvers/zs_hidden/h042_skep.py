"""h042 -- expected net merchant proceeds with a primary processor and one backup retry.

AMBIGUITY RESOLUTIONS (skeptical pass, each tied to the question wording)
-------------------------------------------------------------------------
1. "succeeds with probability 0.35" / "conditional success probability is 0.7":
   plain probabilities (ratios).  "0.02 of the stated amount" / "0.03 of the stated
   amount": plain fractions of the amount, i.e. 0.02 * A, NOT 0.02 percent.  The
   parser nevertheless tolerates a trailing "percent"/"%" (then divides by 100) so a
   re-worded instance does not silently break.
2. Settlement probability per order = p + (1 - p) * s (exactly one retry per primary
   failure; "no order is retried more than once").  Revenue per settlement is the
   GROSS stated amount A; fees are deducted separately, never netted from revenue.
3. Checkpoint 1 "fraction of original attempts expected to settle through the backup
   retry", unit ratio -> (1 - p) * s.  Not s alone (that is conditional on a primary
   failure) and not the count N * (1 - p) * s (unit would be attempts, not a ratio).
4. Primary fee "on every original attempt, whether successful or failed" ->
   N * (r1 * A + f1); fixed fee is per attempt, charged N times.
5. Checkpoint 2 "expected backup processing fees": one retry per primary failure,
   charged "whether successful or failed" -> N * (1 - p) * (r2 * A + f2).
6. Handling: h1 "for every primary failure" applies to ALL primary failures, including
   the ones rescued by the retry -> N * (1 - p) * h1.  h2 is "an additional ... for
   every order where both attempts fail" -> N * (1 - p) * (1 - s) * h2.
7. Checkpoint 3 "expected additional handling cost from terminal failures" mirrors the
   question's word "additional", so it is the h2 component only: N*(1-p)*(1-s)*h2.
   It excludes h1 (which is incurred on rescued orders too) and excludes lost revenue.
8. "pays S once for the batch" -> a single subscription deduction of S.
9. Net = revenue - primary fees - backup fees - h1 handling - h2 handling - S.
   No floor at zero; sign preserved.  Everything stays exact (Fraction); the
   framework rounds the final (2 dp) and each checkpoint (4 dp / 2 dp / 2 dp).
10. Counts N*(1-p) etc. are exact expectations ("treat all probabilities as exact
    scenario expectations"): no rounding of expected counts to whole orders.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h042"

_CUR = r"(?:USD\s*|US\$\s*|\$\s*)?"  # optional currency prefix
_PCT = r"(\s*(?:percent|%))?"        # optional percent suffix (group)


def _num(pattern: str, text: str) -> Fraction:
    """Number captured by ``{N}`` in ``pattern`` (first number group), exact."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return F(m.group(1))


def _rate(pattern: str, text: str) -> Fraction:
    """Probability / fraction: ``{N}`` followed optionally by percent -> ratio."""
    rx = pattern.replace("{N}", f"({NUMBER}){_PCT}")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v /= 100
    return v


def _charge(side: str, text: str) -> tuple[Fraction, Fraction]:
    """(proportional rate as ratio, fixed fee) for 'primary'/'backup' charges."""
    rx = (
        rf"{side} charges\s+{_CUR}({NUMBER}){_PCT}\s+of the stated amount\s+plus\s+"
        rf"(?:a\s+)?fixed fee\s+(?:of\s+)?{_CUR}({NUMBER})"
    )
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"{side} charge clause not found")
    rate = F(m.group(1))
    if m.group(2):
        rate /= 100
    fixed = F(m.group(3))
    return rate, fixed


def solve(text: str, q: dict) -> dict:
    n = _num(r"has\s+{N}\s+original payment attempts", text)
    amount = _num(rf"each for\s+{_CUR}{{N}}", text)
    p = _rate(r"primary processor succeeds with probability\s+{N}", text)
    s = _rate(r"conditional success probability is\s+{N}", text)
    r1, f1 = _charge("primary", text)
    r2, f2 = _charge("backup", text)
    h1 = _num(rf"incurs\s+{_CUR}{{N}}\s+for every primary failure", text)
    h2 = _num(rf"an additional\s+{_CUR}{{N}}\s+for every order where both attempts fail", text)
    sub = _num(rf"pays\s+{_CUR}{{N}}\s+once for the batch", text)

    for name, v in (("p", p), ("s", s)):
        if not (0 <= v <= 1):
            raise ValueError(f"{name}={v} is not a probability")

    q_fail = 1 - p                      # primary-failure probability per order
    retry_settle = q_fail * s           # fraction of orders settled via backup (ratio)
    settle_prob = p + retry_settle      # fraction of orders settled at all
    terminal = q_fail * (1 - s)         # fraction of orders where both attempts fail

    revenue = n * amount * settle_prob
    primary_fees = n * (r1 * amount + f1)
    backup_fees = n * q_fail * (r2 * amount + f2)
    primary_fail_handling = n * q_fail * h1
    terminal_handling = n * terminal * h2

    net = revenue - primary_fees - backup_fees - primary_fail_handling - terminal_handling - sub

    return {
        "final": net,
        "slots": {
            "retry_success_fraction_checkpoint": retry_settle,
            "backup_processing_fees_checkpoint": backup_fees,
            "terminal_failure_cost_checkpoint": terminal_handling,
        },
    }
