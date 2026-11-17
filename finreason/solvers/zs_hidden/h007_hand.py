"""h007: two-bond holding-period-return screen with duration cap; enum winner.

Per bond: received = redemption + aggregate coupons; outlay = clean price + settlement cost
(settlement cost already includes accrued interest/fees -- not added again);
HPR = (received - outlay) / outlay.  Qualifies iff HPR meets the return threshold and
modified duration meets the duration cap (comparison operators parsed from the wording).
Winner = qualifying bond with the higher exact HPR; stated tie-break; Neither if none qualifies.
"""
from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h007"


def _bond(label: str, text: str) -> dict:
    seg_m = re.search(rf"{label} has (.*?)(?:\.\s|\.$)", text, flags=re.S)
    if seg_m is None:
        raise ValueError(f"no description for {label}")
    seg = seg_m.group(1)
    return {
        "redemption": grab(r"redemption cash (?:of )?(?:USD )?{N}", seg),
        "coupons": grab(r"coupon cash (?:of )?(?:USD )?{N}", seg),
        "clean": grab(r"clean price (?:of )?(?:USD )?{N}", seg),
        "settle": grab(r"settlement cost (?:of )?(?:USD )?{N}", seg),
        "dur": grab(r"modified duration (?:of )?{N}", seg),
    }


def _cmp_ok(value: Fraction, op: str, bound: Fraction) -> bool:
    op = op.lower().strip()
    if op in ("at least", "no less than", "not less than", "greater than or equal to", "at or above"):
        return value >= bound
    if op in ("greater than", "strictly greater than", "more than", "above", "exceeds", "strictly above",
              "strictly exceeds", "exceed", "strictly exceed"):
        return value > bound
    if op in ("at most", "no more than", "not more than", "less than or equal to", "at or below",
              "no greater than", "not greater than"):
        return value <= bound
    if op in ("less than", "strictly less than", "below", "strictly below", "under", "fewer than"):
        return value < bound
    raise ValueError(f"unknown comparison {op!r}")


_OPS = (r"strictly greater than|greater than or equal to|greater than|strictly less than|less than or equal to|"
        r"less than|at least|at most|no less than|not less than|no more than|not more than|no greater than|"
        r"not greater than|more than|strictly above|strictly below|at or above|at or below|above|below|"
        r"strictly exceeds|strictly exceed|exceeds|exceed|under")


def solve(text: str, q: dict) -> dict:
    a = _bond("Bond A", text)
    b = _bond("Bond B", text)

    m_ret = re.search(rf"holding-period return (?:is |must be )?({_OPS}) (?:the )?(?:exact )?(?:ratio )?({NUMBER})( percent)?",
                      text, flags=re.S)
    if m_ret is None:
        raise ValueError("return threshold not found")
    ret_op = m_ret.group(1)
    ret_bound = Fraction(m_ret.group(2).replace(",", ""))
    if m_ret.group(3):
        ret_bound /= 100

    m_dur = re.search(rf"its modified duration (?:is |must be )?({_OPS}) ({NUMBER})", text, flags=re.S)
    if m_dur is None:
        raise ValueError("duration cap not found")
    dur_op = m_dur.group(1)
    dur_bound = Fraction(m_dur.group(2).replace(",", ""))

    def evaluate(bd: dict):
        received = bd["redemption"] + bd["coupons"]
        outlay = bd["clean"] + bd["settle"]
        hpr = (received - outlay) / outlay
        ok = _cmp_ok(hpr, ret_op, ret_bound) and _cmp_ok(bd["dur"], dur_op, dur_bound)
        return outlay, hpr, ok

    out_a, hpr_a, ok_a = evaluate(a)
    out_b, hpr_b, ok_b = evaluate(b)

    tie_m = re.search(r"choose (Bond A|Bond B) on (?:an )?(?:exact )?tie", text)
    tie_pick = tie_m.group(1) if tie_m else "Bond A"

    if ok_a and ok_b:
        if hpr_a > hpr_b:
            final = "Bond A"
        elif hpr_b > hpr_a:
            final = "Bond B"
        else:
            final = tie_pick
    elif ok_a:
        final = "Bond A"
    elif ok_b:
        final = "Bond B"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "a_outlay_checkpoint": out_a,
            "b_outlay_checkpoint": out_b,
        },
    }
