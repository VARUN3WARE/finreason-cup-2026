"""h083 -- sell now vs hold one period (two-state), with a scenario-local gain-tax convention.

AMBIGUITY HUNT (resolved from the text before coding)
-----------------------------------------------------
A1. Position size / basis. "selling the complete position" + "complete two-lot basis":
    N = n1 + n2 shares, basis = n1*p1 + n2*p2 (total-position USD). Both lots sell together in
    every branch; no lot selection / no partial sale.
A2. Amount realized. "sale cost reduces amount realized": AR = N * price - total sale cost
    (the current sale cost for the current sale, the "total future sale cost" for both future states).
    The sale cost is a TOTAL (not per share): "sale costs ... are total-position USD".
A3. Taxable gain. "positive gain equals amount realized minus the complete two-lot basis" and the
    convention "gives no loss credit": taxable gain = max(0, AR - basis). Gain tax = ratio * taxable gain.
    The dividend is NOT part of amount realized (it is taxed separately by its own ratio), so it is
    excluded from the gain.
A4. Checkpoints 1-3 are the three taxable gains (current, base-state, downside-state), total-position
    USD, floored at zero, unrounded (framework rounds half-up to cents).
A5. Dividend. "gross terminal dividend is D per share in either state" and "Terminal dividend tax
    ratio is t_d": after-tax dividend = N * D * (1 - t_d), received at the terminal date in both
    states, and included in each state's "future after-tax cash" (it is cash, after tax, at t=1).
A6. After-tax cash. Current: AR0 - gain tax. Future state s: AR_s - gain tax_s + after-tax dividend.
A7. Discounting. "Discount both future after-tax cash states one period using time-value-only rate r":
    PV_s = cash_s / (1 + r)^1. r is a ratio (text: "rates and probabilities are ratios"); a
    "percent" fallback is handled anyway. The current after-tax cash is at t=0 and is NOT discounted.
A8. Probabilities. p_down is stated; p_base = 1 - p_down ("exhaustive" two states).
    Hold value = p_down * PV_down + p_base * PV_base (probability-weighted PRESENT value).
A9. Qualification tests. "at least" => non-strict (>=). Current qualifies on its after-tax cash vs its
    floor; Hold qualifies on the DOWNSIDE-state PV only (not the weighted value) vs its floor.
    Comparison strictness is detected from the wording in case a sibling says "more than"/"exceeds".
A10. Decision. Both qualify -> compare hold weighted PV against current after-tax cash; higher wins;
    exact tie -> "Current sale" (tie token detected from the text, default Current sale).
    Exactly one qualifies -> that one. None -> "Neither".
A11. "exact" everywhere: no rounding inside the computation; Fractions throughout.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h083"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _rate(pattern: str, text: str) -> Fraction:
    """Number captured by pattern; divided by 100 when immediately followed by 'percent' or '%'."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"(\s*(?:percent|%))?"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    return v / 100 if m.group(2) else v


def _first(text: str, patterns: list[str]) -> Fraction:
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _periods(text: str) -> int:
    m = re.search(r"Discount[^.]*?\b(one|two|three|four|five|\d+)\s+periods?", text, flags=re.I)
    if m is None:
        return 1
    w = m.group(1).lower()
    return _WORD_NUM.get(w, int(w) if w.isdigit() else 1)


def _at_least(clause: str) -> bool:
    """True when the qualification clause is non-strict ('at least' / 'no less than' / 'or more')."""
    c = clause.lower()
    if re.search(r"at least|no less than|not less than|or more|or higher|greater than or equal|>=", c):
        return True
    if re.search(r"more than|exceeds|greater than|above|strictly", c):
        return False
    return True  # default to the wording used in this cluster


def _qualifies(value: Fraction, floor: Fraction, non_strict: bool) -> bool:
    return value >= floor if non_strict else value > floor


def _tie_token(text: str) -> str:
    m = re.search(r"choose\s+(Current sale|Hold then sell|Neither)\s+on an exact tie", text)
    return m.group(1) if m else "Current sale"


def solve(text: str, q: dict) -> dict:
    # --- position and basis (A1)
    n1 = grab(r"owns {N} shares bought at", text)
    p1 = grab(r"owns {N} shares bought at {N} per share", text, group=2)
    n2 = grab(r"per share and {N} shares bought at", text)
    p2 = grab(r"per share and {N} shares bought at {N} per share", text, group=2)
    N = n1 + n2
    basis = n1 * p1 + n2 * p2

    # --- current sale (A2)
    price_now = _first(text, [r"now at {N} per share", r"position now at {N}"])
    cost_now = _first(text, [r"now at [^;]*?total sale cost (?:of )?{N}", r"total sale cost (?:of )?{N}"])

    # --- future states
    price_base = grab(r"base terminal sale price is {N}", text)
    price_down = grab(r"downside terminal sale price is {N}", text)
    div_ps = _first(text, [r"gross terminal dividend is {N} per share", r"terminal dividend (?:is|of) {N}"])
    cost_future = _first(text, [r"total future sale cost is {N}", r"future sale cost (?:is|of) {N}"])

    # --- tax ratios, rate, probabilities (A5, A7, A8)
    t_gain = _rate(r"gain tax ratio (?:is |of )?{N}", text)
    t_div = _rate(r"dividend tax ratio (?:is |of )?{N}", text)
    r = _rate(r"time-value-only rate (?:is |of )?{N}", text)
    p_down = _rate(r"downside probability (?:is |of )?{N}", text)
    try:
        p_base = _rate(r"base probability (?:is |of )?{N}", text)
    except ValueError:
        p_base = 1 - p_down
    n_per = _periods(text)

    # --- floors and strictness (A9)
    m_cur = re.search(r"Current sale qualifies when[^.]*?\.", text, flags=re.S)
    m_hold = re.search(r"Holding qualifies when[^.]*?\.", text, flags=re.S)
    cur_clause = m_cur.group(0) if m_cur else ""
    hold_clause = m_hold.group(0) if m_hold else ""
    floor_cur = grab(r"Current sale qualifies when[^.]*?(?:at least|more than|exceeds|above|than) {N}", text)
    floor_hold = grab(r"Holding qualifies when[^.]*?(?:at least|more than|exceeds|above|than) {N}", text)
    cur_non_strict = _at_least(cur_clause)
    hold_non_strict = _at_least(hold_clause)

    # --- gains (A3, A4)
    def taxable_gain(price: Fraction, cost: Fraction) -> Fraction:
        ar = N * price - cost
        g = ar - basis
        return g if g > 0 else Fraction(0)

    def after_tax_sale(price: Fraction, cost: Fraction) -> Fraction:
        ar = N * price - cost
        return ar - t_gain * taxable_gain(price, cost)

    gain_now = taxable_gain(price_now, cost_now)
    gain_base = taxable_gain(price_base, cost_future)
    gain_down = taxable_gain(price_down, cost_future)

    # --- after-tax cash (A6) and present values (A7)
    cash_now = after_tax_sale(price_now, cost_now)
    div_after_tax = N * div_ps * (1 - t_div)
    cash_base = after_tax_sale(price_base, cost_future) + div_after_tax
    cash_down = after_tax_sale(price_down, cost_future) + div_after_tax
    disc = (1 + r) ** n_per
    pv_base = cash_base / disc
    pv_down = cash_down / disc
    hold_value = p_down * pv_down + p_base * pv_base

    # --- decision (A9, A10)
    cur_ok = _qualifies(cash_now, floor_cur, cur_non_strict)
    hold_ok = _qualifies(pv_down, floor_hold, hold_non_strict)
    if cur_ok and hold_ok:
        if hold_value > cash_now:
            final = "Hold then sell"
        elif cash_now > hold_value:
            final = "Current sale"
        else:
            final = _tie_token(text)
    elif cur_ok:
        final = "Current sale"
    elif hold_ok:
        final = "Hold then sell"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "current_gain_checkpoint": gain_now,
            "base_gain_checkpoint": gain_base,
            "downside_gain_checkpoint": gain_down,
        },
    }
