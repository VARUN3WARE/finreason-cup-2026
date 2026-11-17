"""h072 -- two-scenario residual-value revision with three declining-balance subperiods.

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED (textual evidence in quotes):

1. Starting balance for depreciation.
   "An asset has original cost C and accumulated depreciation of D ... Scenario X revises residual value to R"
   -> the balance above residual is the CARRYING AMOUNT minus the revised residual: B0 = (C - D) - R.
   Accumulated depreciation is given precisely so that the carrying amount (not original cost) is the base, and
   "residual value itself is not depreciated" confirms the base excludes R.

2. Ratio unit. "per-subperiod depreciation ratio 0.28" -> plain ratio, used as-is (not a percent).

3. Declining vs straight-line. "In each subperiod, the scenario-specific ratio applies AGAIN to the balance above
   residual value" -> each stage applies r to the then-current balance above residual (which has shrunk after the
   previous stage), i.e. geometric decline: stage-k depreciation = r * B0 * (1-r)^(k-1).
   Cumulative three-stage depreciation = B0 * (1 - (1-r)^n); remaining balance above residual = B0 * (1-r)^n.
   The checkpoint's "retention factor" wording presupposes this compounding structure.

4. Number of stages. "exactly three equal sequential subperiods" -> n = 3, parsed from the word ("three") with a
   digit fallback; never hardcoded for a given instance.

5. Qualification thresholds (units: USD millions, same as the inputs).
   "exact cumulative three-stage depreciation is at most T1" -> cum <= T1 (non-strict);
   "remaining depreciable balance above residual is at least T2" -> rem >= T2 (non-strict), where rem is measured
   AFTER the three stages. Both must hold ("qualifies only if ... and ...").
   The comparator words are parsed, so "less than"/"more than"/"exceeds" would become strict if ever worded so.

6. Selection. "Return the qualifying scenario with lower exact cumulative depreciation, choose Scenario A on an
   exact tie, or return Neither scenario when neither qualifies."
   -> among qualifiers pick the smaller exact Fraction; if equal -> "Scenario A"; a sole qualifier wins by default;
   no qualifier -> "Neither scenario". No rounding anywhere ("exact" is explicit).

7. Checkpoint "Scenario A's one-subperiod balance-retention factor" (ratio, 6 dp half-up).
   -> the fraction of the balance above residual retained after ONE subperiod = 1 - r_A.
   Not (1-r_A)^3 ("one-subperiod" is explicit) and not a retention of the whole carrying amount including residual
   (the "balance" that the ratio acts on is the balance above residual). The seven-digit ratios (0.1999995 ->
   0.8000005, 0.2108766 -> 0.7891234) are built so that six-place half-up rounding is the real test, which only
   makes sense for 1 - r_A. Returned unrounded; the framework rounds.

8. Degenerate branch (not present in these instances): if the carrying amount does not exceed the revised residual
   (B0 <= 0) there is no balance above residual to depreciate, so depreciation is 0 and the remaining balance is
   B0 (<= 0), which fails any positive "at least" threshold.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h072"

_WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _stages(text: str) -> int:
    m = re.search(r"exactly\s+(\w+)\s+equal\s+sequential\s+subperiods", text, flags=re.I)
    if m is None:
        m = re.search(r"(\w+)\s+(?:equal\s+)?(?:sequential\s+)?subperiods", text, flags=re.I)
    if m is None:
        return 3
    tok = m.group(1).lower()
    if tok in _WORD_NUMS:
        return _WORD_NUMS[tok]
    if tok.isdigit():
        return int(tok)
    return 3


def _threshold(text: str, lead: str) -> tuple[Fraction, str]:
    """Return (threshold value, comparator kind) for the phrase that follows ``lead``.

    kind is one of 'le', 'lt', 'ge', 'gt'.
    """
    cmp_rx = (
        r"(at most|no more than|not more than|not exceeding|does not exceed|less than|below|under|"
        r"at least|no less than|not less than|more than|greater than|above|over|exceeds)"
    )
    m = re.search(lead + r"[^.;]*?\b" + cmp_rx + r"\s+(?:USD\s+)?(" + NUMBER + ")", text, flags=re.I | re.S)
    if m is None:
        raise ValueError(f"threshold not found after {lead!r}")
    word = m.group(1).lower()
    value = F(m.group(2))
    if word in ("at most", "no more than", "not more than", "not exceeding", "does not exceed"):
        return value, "le"
    if word in ("less than", "below", "under"):
        return value, "lt"
    if word in ("at least", "no less than", "not less than"):
        return value, "ge"
    return value, "gt"


def _passes(x: Fraction, thr: Fraction, kind: str) -> bool:
    if kind == "le":
        return x <= thr
    if kind == "lt":
        return x < thr
    if kind == "ge":
        return x >= thr
    return x > thr


def _scenario(carrying: Fraction, residual: Fraction, ratio: Fraction, n: int) -> tuple[Fraction, Fraction]:
    """Return (cumulative n-stage depreciation, remaining balance above residual) -- exact."""
    b0 = carrying - residual
    if b0 <= 0:
        return Fraction(0), b0
    retained = (1 - ratio) ** n
    remaining = b0 * retained
    cumulative = b0 - remaining
    return cumulative, remaining


def solve(text: str, q: dict) -> dict:
    cost = grab(r"original cost(?: of)?(?: USD)? {N}", text)
    acc_dep = grab(r"accumulated depreciation(?: of)?(?: USD)? {N}", text)

    res_a = grab(r"Scenario A[^.;]*?residual value (?:to|of) {N}", text)
    ratio_a = grab(r"Scenario A[^.;]*?depreciation ratio(?: of)? {N}", text)
    m_b = re.search(
        r"Scenario B\s+(?:uses|applies|revises residual value to)\s+(" + NUMBER + r")\s+and\s+"
        r"(?:applies\s+)?(?:per-subperiod\s+depreciation\s+ratio\s+)?(" + NUMBER + ")",
        text,
        flags=re.S,
    )
    if m_b is None:
        raise ValueError("Scenario B parameters not found")
    res_b, ratio_b = F(m_b.group(1)), F(m_b.group(2))

    n = _stages(text)
    dep_thr, dep_kind = _threshold(text, r"cumulative[^.;]*?depreciation is")
    rem_thr, rem_kind = _threshold(text, r"remaining depreciable balance above residual is")

    carrying = cost - acc_dep
    cum_a, rem_a = _scenario(carrying, res_a, ratio_a, n)
    cum_b, rem_b = _scenario(carrying, res_b, ratio_b, n)

    ok_a = _passes(cum_a, dep_thr, dep_kind) and _passes(rem_a, rem_thr, rem_kind)
    ok_b = _passes(cum_b, dep_thr, dep_kind) and _passes(rem_b, rem_thr, rem_kind)

    if ok_a and ok_b:
        final = "Scenario A" if cum_a <= cum_b else "Scenario B"  # exact tie -> Scenario A
    elif ok_a:
        final = "Scenario A"
    elif ok_b:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    return {
        "final": final,
        "slots": {"a_one_stage_retention_factor_checkpoint": 1 - ratio_a},
    }
