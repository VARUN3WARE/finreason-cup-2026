"""Cluster h007 -- two-bond holding-period-return screen with a duration cap.

AMBIGUITY RESOLUTIONS (each tied to the question wording)
----------------------------------------------------------
1. Total acquisition outlay = clean price + settlement cost, NOTHING ELSE.
   Text: "Each settlement cost is all acquisition cash beyond the clean quote,
   including accrued interest and fees where applicable; do not add those
   amounts again." and "total acquisition outlay as clean price plus
   settlement cost".  So accrued interest is NOT added on top; no dirty-price
   reconstruction.  Both checkpoints are exactly this sum, in USD (the prices
   are quoted in plain currency units, so no scaling).
2. Total received cash = expected redemption cash + aggregate coupon cash
   ("define total received cash as redemption plus aggregate coupons").
   No discounting, no reinvestment -- it is a simple cash sum over the
   "common holding horizon".
3. Holding-period return = (received - outlay) / outlay, a plain RATIO
   (dimensionless), compared against "the exact ratio 0.05" -- i.e. the
   threshold is already a ratio, not a percent.  (A defensive fallback divides
   by 100 only if the threshold phrase says "percent".)
4. Return threshold is NON-STRICT: "at least the exact ratio X"  ->  hpr >= X.
   Duration cap is NON-STRICT: "modified duration is at most Y"  ->  dur <= Y.
   Both are evaluated with exact Fractions ("its exact holding-period
   return"); no rounding anywhere in the chain -- instance 3 has A's return
   at 20.208/102 = 0.19811... just below 0.2, so exactness is load-bearing.
5. Qualification is a conjunction: BOTH the return test AND the duration test
   must pass ("qualifies only if ... and ...").
6. Selection among qualifiers: if both qualify, pick the higher exact return;
   on an exact tie pick Bond A ("choose Bond A on an exact tie").  If exactly
   one qualifies, return it regardless of how its return compares to the
   non-qualifier.  If none qualifies -> "Neither".
7. "Both durations use the same acquisition-date convention and basis" is a
   no-op statement: the durations are directly comparable to the cap as given.
8. The enum tokens are exactly "Bond A", "Bond B", "Neither" (case-sensitive).
9. Parsing: each bond's five figures are read from its own "Bond X has ..."
   sentence (segment-anchored so Bond A's and Bond B's values can never be
   confused), the threshold from "at least ... {N}" and the cap from
   "modified duration is at most {N}".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, after, grab

TEMPLATE_ID = "h007"

_SENT_END = re.compile(r"\.(?=\s|$)")  # a period that ends a sentence (not a decimal point)


def _segment(text: str, start_phrase: str) -> str:
    """The sentence that starts with ``start_phrase`` (e.g. 'Bond A has')."""
    i = text.index(start_phrase)
    m = _SENT_END.search(text, i)
    j = m.end() if m else len(text)
    return text[i:j]


def _bond(text: str, label: str) -> dict[str, Fraction]:
    seg = _segment(text, f"Bond {label} has")
    return {
        "redemption": grab(r"redemption cash\s*(?:of\s*)?{N}", seg),
        "coupons": grab(r"coupon cash\s*(?:of\s*)?{N}", seg),
        "clean": grab(r"clean price\s*(?:of\s*)?{N}", seg),
        "settle": grab(r"settlement cost\s*(?:of\s*)?{N}", seg),
        "duration": grab(r"modified duration\s*(?:of\s*)?{N}", seg),
    }


def _threshold(text: str) -> Fraction:
    """Return threshold as a ratio.  Primary wording: 'at least the exact ratio 0.05'."""
    m = re.search(r"return is at least[^.\d-]*?(" + NUMBER + r")(\s*percent)?", text)
    if m is None:
        return after(text, "at least")
    v = F(m.group(1))
    return v / 100 if m.group(2) else v


def _duration_cap(text: str) -> Fraction:
    return grab(r"modified duration is at most\s*{N}", text)


def solve(text: str, q: dict) -> dict:
    a = _bond(text, "A")
    b = _bond(text, "B")
    thr = _threshold(text)
    cap = _duration_cap(text)

    def outlay(x: dict[str, Fraction]) -> Fraction:
        return x["clean"] + x["settle"]

    def received(x: dict[str, Fraction]) -> Fraction:
        return x["redemption"] + x["coupons"]

    def hpr(x: dict[str, Fraction]) -> Fraction:
        o = outlay(x)
        return (received(x) - o) / o

    a_out, b_out = outlay(a), outlay(b)
    a_r, b_r = hpr(a), hpr(b)

    a_ok = a_r >= thr and a["duration"] <= cap  # "at least" / "at most": non-strict
    b_ok = b_r >= thr and b["duration"] <= cap

    if a_ok and b_ok:
        final = "Bond A" if a_r >= b_r else "Bond B"  # exact tie -> Bond A
    elif a_ok:
        final = "Bond A"
    elif b_ok:
        final = "Bond B"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "a_outlay_checkpoint": a_out,
            "b_outlay_checkpoint": b_out,
        },
    }
