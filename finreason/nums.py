"""Exact number extraction helpers for solver modules.

All helpers return ``Fraction`` values; solvers must never use floats.
"""

from __future__ import annotations

import re
from fractions import Fraction

# Signed decimal or simple rational; commas inside numbers are tolerated.
NUMBER = r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?(?:/\d+)?"
NUMBER_RE = re.compile(NUMBER)


def F(text: str | int | Fraction) -> Fraction:
    if isinstance(text, Fraction):
        return text
    if isinstance(text, int):
        return Fraction(text)
    return Fraction(text.replace(",", ""))


def numbers(text: str) -> list[Fraction]:
    """All numbers in reading order."""
    return [F(m.group(0)) for m in NUMBER_RE.finditer(text)]


def after(text: str, phrase: str, nth: int = 0) -> Fraction:
    """First number appearing after the nth occurrence of ``phrase``."""
    start = -1
    for _ in range(nth + 1):
        start = text.index(phrase, start + 1)
    m = NUMBER_RE.search(text, start + len(phrase))
    if m is None:
        raise ValueError(f"no number after {phrase!r}")
    return F(m.group(0))


def before(text: str, phrase: str, nth: int = 0) -> Fraction:
    """Last number appearing before the nth occurrence of ``phrase``."""
    start = -1
    for _ in range(nth + 1):
        start = text.index(phrase, start + 1)
    found = list(NUMBER_RE.finditer(text, 0, start))
    if not found:
        raise ValueError(f"no number before {phrase!r}")
    return F(found[-1].group(0))


def grab(pattern: str, text: str, group: int | str = 1) -> Fraction:
    """Regex search where ``{N}`` in the pattern stands for a number capture."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return F(m.group(group))


def grab_all(pattern: str, text: str) -> list[Fraction]:
    """All groups of the first match of ``pattern`` (with ``{N}`` = number)."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return [F(g) for g in m.groups() if g is not None]


def pct(value: Fraction) -> Fraction:
    """Percent number -> ratio."""
    return value / 100


def ipow(base: Fraction, exponent: Fraction | int) -> Fraction:
    """Exact integer power; raises if the exponent is not an integer."""
    e = Fraction(exponent)
    if e.denominator != 1:
        raise ValueError(f"non-integer exponent {e}")
    return Fraction(base) ** int(e)


# --- Irrational operations (roots, logs, exp): high-precision Decimal, returned as Fraction.
# Only use these when the question genuinely requires a non-integer power / log / exp.
from decimal import Decimal, localcontext  # noqa: E402

_PREC = 80


def _dec(x: Fraction) -> Decimal:
    return Decimal(x.numerator) / Decimal(x.denominator)


def real_pow(base: Fraction, exponent: Fraction) -> Fraction:
    """base ** exponent for any rational exponent (base > 0), 80-digit precision."""
    exponent = Fraction(exponent)
    if exponent.denominator == 1:
        return Fraction(base) ** int(exponent)
    with localcontext() as ctx:
        ctx.prec = _PREC
        return Fraction(_dec(Fraction(base)) ** _dec(exponent))


def root(x: Fraction, n: int) -> Fraction:
    return real_pow(Fraction(x), Fraction(1, n))


def ln(x: Fraction) -> Fraction:
    with localcontext() as ctx:
        ctx.prec = _PREC
        return Fraction(_dec(Fraction(x)).ln())


def exp(x: Fraction) -> Fraction:
    with localcontext() as ctx:
        ctx.prec = _PREC
        return Fraction(_dec(Fraction(x)).exp())


def sqrt(x: Fraction) -> Fraction:
    with localcontext() as ctx:
        ctx.prec = _PREC
        return Fraction(_dec(Fraction(x)).sqrt())
