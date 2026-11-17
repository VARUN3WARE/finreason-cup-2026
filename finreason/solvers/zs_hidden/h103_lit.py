"""Hidden cluster h103 -- literal transcription solver.

Fictional transaction-review policy: three related cash transactions, an aggregate
review threshold, a largest-to-history spike ratio compared against a baseline spike
threshold that is reduced by a fixed fraction at each of N sequential stages, plus two
recorded critical flags.  Final answer is the policy route (enum); the single
checkpoint is the one-stage threshold-retention factor (1 - fraction).

Every sentence of the question is transcribed, in order, into a variable or rule.
All arithmetic is exact (Fraction); nothing is rounded internally.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, numbers

TEMPLATE_ID = "h103"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _count(token: str) -> int:
    """Word ('three') or digit ('3') count -> int."""
    t = token.strip().lower()
    if t in _WORDS:
        return _WORDS[t]
    return int(t)


def _bool(token: str) -> bool:
    t = token.strip().lower()
    if t == "true":
        return True
    if t == "false":
        return False
    raise ValueError(f"not a boolean token: {token!r}")


def solve(text: str, q: dict) -> dict:
    # S1 "Apply the fictional scenario-local transaction-review policy given here, not current
    #     law or regulatory guidance."  -> only the rules stated below are applied.

    # S2 "Three related cash transactions are 7, 2, and 1."
    m = re.search(r"related cash transactions are (.*?)\.(?:\s|$)", text, flags=re.S)
    if m is None:
        raise ValueError("transaction list not found")
    transactions = numbers(m.group(1))
    if not transactions:
        raise ValueError("no transactions parsed")

    # S3 "The aggregate review threshold is 15."
    aggregate_review_threshold = grab(r"aggregate review threshold is {N}", text)

    # S4 "The customer's historical average cash transaction is 3, and the baseline
    #     largest-to-history spike-ratio threshold is 2."
    historical_average = grab(r"historical average cash transaction is {N}", text)
    baseline_spike_threshold = grab(r"spike-ratio threshold is {N}", text)

    # S5 "At each of exactly three sequential adjustment stages, reduce the surviving spike
    #     threshold by fraction 0.23 of its then-current value, with no replenishment between
    #     stages; the effective threshold is the baseline multiplied by one minus that fraction
    #     three successive times."
    ms = re.search(r"each of exactly (\w+) sequential adjustment stages", text)
    stages = _count(ms.group(1)) if ms else None
    mt = re.search(r"one minus that fraction (\w+) successive times", text)
    times = _count(mt.group(1)) if mt else None
    if stages is None and times is None:
        raise ValueError("number of adjustment stages not found")
    if stages is not None and times is not None and stages != times:
        raise ValueError(f"stage count mismatch: {stages} vs {times}")
    n_stages = stages if stages is not None else times

    mf = re.search(rf"by fraction ({NUMBER}) of its then-current value", text)
    if mf is not None:
        reduction_fraction = F(mf.group(1))
    else:  # defensive fallback: reduction stated in percent
        reduction_fraction = grab(r"by {N} percent of its then-current value", text) / 100

    # one-stage threshold-retention factor = "one minus that fraction"
    retention_factor = 1 - reduction_fraction

    # stage-by-stage: surviving threshold reduced by the fraction of its then-current value,
    # no replenishment between stages
    surviving_threshold = Fraction(baseline_spike_threshold)
    for _ in range(n_stages):
        surviving_threshold = surviving_threshold - reduction_fraction * surviving_threshold
    # stated closed form: baseline multiplied by (1 - fraction) n successive times
    effective_threshold = baseline_spike_threshold * retention_factor ** n_stages
    assert surviving_threshold == effective_threshold

    # S6 "Define the spike ratio as the largest transaction divided by the historical average."
    largest_transaction = max(transactions)
    spike_ratio = largest_transaction / historical_average

    # S7 "The policy also records true and false."  -> the two critical flags
    mflags = re.search(r"policy also records (\w+) and (\w+)", text, flags=re.I)
    if mflags is None:
        raise ValueError("critical flags not found")
    critical_flag_1 = _bool(mflags.group(1))
    critical_flag_2 = _bool(mflags.group(2))

    # S8 "Return Enhanced review when aggregate volume strictly exceeds its threshold and the
    #     spike ratio strictly exceeds the effective threshold, or when either critical flag
    #     is true."
    aggregate_volume = sum(transactions, Fraction(0))
    aggregate_test = aggregate_volume > aggregate_review_threshold
    spike_test = spike_ratio > effective_threshold
    either_flag = critical_flag_1 or critical_flag_2

    # S9 "Otherwise return Standard review."
    if (aggregate_test and spike_test) or either_flag:
        route = "Enhanced review"
    else:
        route = "Standard review"

    # S10 "Report the one-stage threshold-retention factor independently using half-up
    #      rounding to six decimals, then return the exact policy route."
    #      -> unrounded exact value; framework applies half-up to 6 dp.
    return {
        "final": route,
        "slots": {
            "spike_threshold_residual_factor_checkpoint": retention_factor,
        },
    }
