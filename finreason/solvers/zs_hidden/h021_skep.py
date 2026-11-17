"""h021 -- target levered beta via zero-debt-beta Hamada unlever / average / relever.

AMBIGUITY RESOLUTIONS (all from the question text):
 1. Checkpoint "tax-adjusted debt term used in its Hamada factor": the factor is
    worded "[equity plus (one minus tax rate) times debt] divided by equity", so the
    debt TERM of that bracket is (1 - t) * D.  Slot unit is "usd", so it is the USD
    amount (1 - t) * D, not the ratio (1 - t) * D / E and not the whole bracket.
 2. Tax rate is quoted as a plain decimal ("tax rate 0.2"), so it is used as-is.
    Guard: a "percent"/"%" suffix or a value > 1 is treated as a percent and /100.
 3. Each entity uses its OWN tax rate (A's, B's, target's) -- "marginal corporate
    tax rate" is listed per comparable and "tax rate" for the target.
 4. "equally weighted" / "unweighted arithmetic mean": simple (bU_A + bU_B) / 2,
    not an equity- or value-weighted average.
 5. Order: unlever each comparable (bL / factor), average the UNLEVERED betas,
    then multiply by the target factor of the same form -- exactly as worded.
 6. Debt beta is zero (pure Hamada), ignore cash / preferred / other adjustments.
 7. No rounding anywhere inside the chain; final and checkpoints returned exact.
 8. Comparable B's values are "corresponding values" in the same order as A's
    (levered beta, debt, equity, tax rate); parsed positionally from B's sentence,
    with a labeled parse attempted first in case an instance labels them.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, numbers

TEMPLATE_ID = "h021"

_SENT_SPLIT = re.compile(r"\.\s+(?=[A-Z])")


def _segments(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text)]


def _segment_starting(text: str, prefix: str) -> str:
    for s in _segments(text):
        if s.lower().startswith(prefix.lower()):
            return s
    raise ValueError(f"no sentence starting with {prefix!r}")


def _tax_rate(seg: str) -> Fraction:
    m = re.search(rf"tax rate (?:of )?({NUMBER})\s*(percent|%)?", seg)
    if m is None:
        raise ValueError("tax rate not found")
    t = F(m.group(1))
    if m.group(2) or t > 1:
        t = t / 100
    return t


def _labeled(seg: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    beta = grab(r"levered beta (?:of )?{N}", seg)
    debt = grab(r"debt market value (?:of )?{N}", seg)
    equity = grab(r"equity market value (?:of )?{N}", seg)
    tax = _tax_rate(seg)
    return beta, debt, equity, tax


def _comparable(text: str, label: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    seg = _segment_starting(text, f"Comparable {label}")
    if "levered beta" in seg and "debt market value" in seg:
        return _labeled(seg)
    # "corresponding values" -- same order as comparable A: beta, debt, equity, tax
    vals = numbers(seg)
    if len(vals) != 4:
        raise ValueError(f"expected 4 values for comparable {label}, got {vals}")
    beta, debt, equity, tax = vals
    if re.search(rf"{NUMBER}\s*(percent|%)\s*\.?$", seg) or tax > 1:
        tax = tax / 100
    return beta, debt, equity, tax


def _target(text: str) -> tuple[Fraction, Fraction, Fraction]:
    seg = _segment_starting(text, "The target has")
    debt = grab(r"debt market value (?:of )?{N}", seg)
    equity = grab(r"equity market value (?:of )?{N}", seg)
    tax = _tax_rate(seg)
    return debt, equity, tax


def _tax_adjusted_debt(debt: Fraction, tax: Fraction) -> Fraction:
    return (1 - tax) * debt


def _factor(debt: Fraction, equity: Fraction, tax: Fraction) -> Fraction:
    # [E + (1 - t) D] / E
    return (equity + _tax_adjusted_debt(debt, tax)) / equity


def solve(text: str, q: dict) -> dict:
    bl_a, d_a, e_a, t_a = _comparable(text, "A")
    bl_b, d_b, e_b, t_b = _comparable(text, "B")
    d_t, e_t, t_t = _target(text)

    tad_a = _tax_adjusted_debt(d_a, t_a)
    tad_b = _tax_adjusted_debt(d_b, t_b)

    bu_a = bl_a / _factor(d_a, e_a, t_a)
    bu_b = bl_b / _factor(d_b, e_b, t_b)
    bu_mean = (bu_a + bu_b) / 2

    beta_target = bu_mean * _factor(d_t, e_t, t_t)

    return {
        "final": beta_target,
        "slots": {
            "comparable_a_tax_adjusted_debt_checkpoint": tad_a,
            "comparable_b_tax_adjusted_debt_checkpoint": tad_b,
        },
    }
