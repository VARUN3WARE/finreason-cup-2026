"""Render exact Fraction results into the frozen Task 1 value syntax."""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any, Mapping


def to_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise TypeError("bool is not numeric")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, float):
        # Floats are a solver bug: exact arithmetic is required everywhere.
        raise TypeError(f"float result {value!r}; use Fraction")
    raise TypeError(f"unsupported numeric type {type(value).__name__}")


def exact_text(value: Fraction) -> str:
    """Finite decimal if terminating, else irreducible numerator/denominator."""
    den = value.denominator
    twos = fives = 0
    while den % 2 == 0:
        den //= 2
        twos += 1
    while den % 5 == 0:
        den //= 5
        fives += 1
    if den != 1:
        return f"{value.numerator}/{value.denominator}"
    places = max(twos, fives)
    scaled = abs(value.numerator) * 2 ** (places - twos) * 5 ** (places - fives)
    whole, frac = divmod(scaled, 10**places)
    sign = "-" if value < 0 else ""
    if places == 0 or frac == 0:
        return f"{sign}{whole}"
    return f"{sign}{whole}.{f'{frac:0{places}d}'.rstrip('0')}"


def round_half_up(value: Fraction, places: int) -> Fraction:
    scale = 10**places
    num = value.numerator * scale
    den = value.denominator
    if num >= 0:
        rounded = (2 * num + den) // (2 * den)
    else:
        rounded = -((2 * (-num) + den) // (2 * den))
    return Fraction(rounded, scale)


def half_up_text(value: Fraction, places: int) -> str:
    rounded = round_half_up(value, places)
    scale = 10**places
    n = rounded.numerator * (scale // rounded.denominator)
    sign = "-" if n < 0 else ""
    whole, frac = divmod(abs(n), scale)
    if places == 0:
        text = f"{sign}{whole}"
    else:
        text = f"{sign}{whole}.{frac:0{places}d}"
    return text


def render(value: Any, spec: Mapping[str, Any]) -> str:
    if spec["type"] == "enum":
        text = str(value)
        if text not in spec["allowed_values"]:
            raise ValueError(f"enum value {text!r} not in {spec['allowed_values']}")
        return text
    frac = to_fraction(value)
    rounding = spec["rounding"]
    if rounding["mode"] == "exact":
        return exact_text(frac)
    if rounding["mode"] == "half_up":
        return half_up_text(frac, rounding["decimal_places"])
    raise ValueError(f"unsupported rounding {rounding}")
