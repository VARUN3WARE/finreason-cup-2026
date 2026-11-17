import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.basel.multi_requirement.advanced.v1"

_INCL = r"at least|no less than|not less than|greater than or equal to|minimum of"
_STRICT = r"more than|greater than|above|exceed|exceeds|strictly above"


def _rule(text: str, subject: str) -> tuple[Fraction, bool]:
    """Threshold percent for a named requirement and whether it is strict."""
    m = re.search(
        subject + r"\s+(?:must\s+(?:be\s+)?)?(" + _INCL + r"|" + _STRICT + r")\s+(" + NUMBER + r") percent",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError(f"requirement for {subject!r} not found")
    op = m.group(1)
    strict = re.fullmatch(_INCL, op) is None
    return F(m.group(2)), strict


def _check(num: Fraction, den: Fraction, thr_pct: Fraction, strict: bool) -> bool:
    # num / den * 100 vs threshold; cross-multiplied form avoids division by zero (den > 0 assumed)
    if den != 0:
        v = num / den * 100
    else:
        v = None
    if v is None:
        lhs, rhs = num * 100, thr_pct * den
        return lhs > rhs if strict else lhs >= rhs
    return v > thr_pct if strict else v >= thr_pct


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    t1 = grab(r"Tier 1 capital is {N}", text)
    exposure = grab(r"Exposure is {N}", text)
    total_cap = grab(r"Total capital is {N}", text)
    rwa = grab(r"Risk-weighted assets (?:are|is) {N}", text)
    liq = grab(r"Liquidity assets (?:are|is) {N}", text)
    outflows = grab(r"Net outflows (?:are|is) {N}", text)

    lev_thr, lev_strict = _rule(text, r"Leverage")
    cap_thr, cap_strict = _rule(text, r"total capital")
    liq_thr, liq_strict = _rule(text, r"liquidity")

    lev_ok = _check(t1, exposure, lev_thr, lev_strict)
    cap_ok = _check(total_cap, rwa, cap_thr, cap_strict)
    liq_ok = _check(liq, outflows, liq_thr, liq_strict)
    final = lev_ok and cap_ok and liq_ok
    return {
        "final": _tok(final),
        "slots": {"leverage_met": _tok(lev_ok), "capital_met": _tok(cap_ok), "liquidity_met": _tok(liq_ok)},
    }
