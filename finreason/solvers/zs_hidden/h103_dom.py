"""h103 -- fictional scenario-local transaction-review policy (cash-structuring / spike screen).

FINANCE MODEL (written before the code)
=======================================
Economic setting: an AML-style "structuring" screen applied to a customer's three related cash
transactions.  The policy is FICTIONAL and scenario-local: only the rules in the text apply (no
real-world reporting thresholds, no regulatory guidance).

Inputs and how each number enters
---------------------------------
  t1, t2, t3   the three related cash transactions (currency units never matter: only the sum,
               the maximum and ratios to the historical average are used).
  T_agg        "aggregate review threshold": compared with the SUM of the three transactions.
  H            customer's historical average cash transaction: the DENOMINATOR of the spike ratio.
  B            baseline largest-to-history spike-ratio threshold: the STARTING value of the threshold
               that the spike ratio is compared with.
  f            per-stage reduction fraction (e.g. 0.23 = 23%): at each adjustment stage the
               SURVIVING threshold is reduced by f of its THEN-CURRENT value.
  n            number of sequential stages ("exactly three"); no replenishment between stages.
  k1, k2       the two critical flags ("The policy also records <k1> and <k2>"), booleans.

Derived quantities
------------------
  A = t1 + t2 + t3                      aggregate volume
  L = max(t1, t2, t3)                   largest transaction
  S = L / H                             spike ratio  ("largest transaction divided by the historical
                                        average", exactly as defined in the text)
  r = 1 - f                             one-stage threshold-retention factor (fraction RETAINED after
                                        one stage).  THIS IS THE CHECKPOINT: reported half-up to 6 dp by
                                        the framework, but the unrounded exact rational is returned and
                                        the unrounded r is what feeds the effective threshold ("independently").
  E = B * r**n                          effective spike threshold.  Stages COMPOUND multiplicatively
                                        (each stage multiplies the current threshold by 1 - f); the text
                                        itself spells it out: "baseline multiplied by one minus that
                                        fraction three successive times".  NOT additive (not B*(1 - n*f)).

Decision rule (strict inequalities exactly as worded)
-----------------------------------------------------
  Enhanced review  iff   (A > T_agg  AND  S > E)   OR   k1 is true   OR   k2 is true
  Standard review  otherwise.
  * "strictly exceeds" -> '>' (a tie is NOT an exceedance), on both the aggregate and the spike test.
  * The critical flags are a standalone override ("..., or when either critical flag is true"), i.e. the
    grouping is (volume AND spike) OR flags -- the flags are not an extra AND-condition.

Overrides of standard conventions
---------------------------------
  * None numerically: no percent conversion (f is already a fraction, 0.23 not 23), no day counts, no
    discounting.  The only "override" is that the scenario-local policy replaces any real-law notion of
    a cash-reporting threshold.
  * Everything is exact: Fraction arithmetic only (f such as 0.1999995 and 0.1876547 are 7-decimal
    values; r = 0.8000005 sits exactly on a half-up rounding boundary at 6 dp, so a float would be wrong).

Checkpoint (single slot): spike_threshold_residual_factor_checkpoint = r = 1 - f   (ratio, 6 dp half-up
applied by the framework result_spec).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab, numbers

TEMPLATE_ID = "h103"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _count(token: str) -> int:
    token = token.strip().lower()
    if token in _WORD_NUM:
        return _WORD_NUM[token]
    return int(token)


def _stage_count(text: str) -> int:
    """Number of sequential adjustment stages ("exactly three sequential adjustment stages")."""
    m = re.search(r"exactly\s+(\w+)\s+sequential\s+adjustment\s+stages?", text, flags=re.I)
    if m:
        return _count(m.group(1))
    m = re.search(r"one minus that fraction\s+(\w+)\s+successive\s+times", text, flags=re.I)
    if m:
        return _count(m.group(1))
    raise ValueError("stage count not found")


def _transactions(text: str) -> list[Fraction]:
    """The related cash transactions listed after 'cash transactions are'."""
    m = re.search(r"cash transactions are\s+(.+?)\.(?=\s|$)", text, flags=re.S)
    if m is None:
        raise ValueError("transaction list not found")
    vals = numbers(m.group(1))
    if not vals:
        raise ValueError("no transaction amounts")
    return vals


def _flags(text: str) -> list[bool]:
    """Boolean critical flags from 'The policy also records <true|false> and <true|false>.'"""
    m = re.search(r"also records\s+([^.]*)\.", text, flags=re.I)
    if m is None:
        raise ValueError("flag clause not found")
    toks = re.findall(r"\b(true|false)\b", m.group(1), flags=re.I)
    if not toks:
        raise ValueError("no flag values")
    return [t.lower() == "true" for t in toks]


def solve(text: str, q: dict) -> dict:
    # ---- parse (anchored on the surrounding words, never on instance values) ----
    txns = _transactions(text)
    t_agg = grab(r"aggregate review threshold is {N}", text)
    hist = grab(r"historical average cash transaction is {N}", text)
    base = grab(r"baseline largest-to-history spike-ratio threshold is {N}", text)
    frac = grab(r"reduce the surviving spike threshold by fraction {N} of its then-current value", text)
    stages = _stage_count(text)
    flags = _flags(text)

    # ---- model ----
    aggregate = sum(txns, Fraction(0))
    largest = max(txns)
    spike_ratio = largest / hist                      # largest / historical average
    retained = Fraction(1) - frac                     # one-stage retention factor (checkpoint, unrounded)
    effective = base * retained ** stages             # compounding: baseline * (1 - f) ** n
    volume_breach = aggregate > t_agg                 # strictly exceeds
    spike_breach = spike_ratio > effective            # strictly exceeds
    enhanced = (volume_breach and spike_breach) or any(flags)

    return {
        "final": "Enhanced review" if enhanced else "Standard review",
        "slots": {"spike_threshold_residual_factor_checkpoint": retained},
    }
