"""h006 -- partially exposed portfolio: signed factor shock needed for a target value change.

Literal transcription of the question text:
  "A portfolio is worth V, but only share s is exposed to one factor."
      -> V (portfolio value), s (exposed share; a plain fraction unless written as a percent)
  "The exposed portion has signed sensitivity b."
      -> b (signed sensitivity of the exposed portion to the factor)
  "Determine the signed factor shock required to produce target portfolio value change dV,
   and report that shock as a percentage."
      -> exposed value E = V * s                     (checkpoint: exposed_value_checkpoint, usd)
         value change = E * b * shock  =>  shock = dV / (E * b)
         final = shock * 100                          (percent, sign preserved)
"""

from fractions import Fraction

from finreason.nums import grab, NUMBER  # noqa: F401
import re

TEMPLATE_ID = "h006"


def _num_with_optional_percent(pattern: str, text: str) -> Fraction:
    """Grab the number in ``pattern``; if it is immediately followed by 'percent' or '%', convert to a ratio."""
    rx = pattern.replace("{N}", f"({NUMBER})" + r"\s*(%|percent\b)?")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    val = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        val /= 100
    return val


def solve(text: str, q: dict) -> dict:
    # Sentence 1: portfolio value and exposed share.
    V = grab(r"portfolio is worth\s+(?:USD\s+|\$\s*)?{N}", text)
    s = _num_with_optional_percent(r"share\s+{N}", text)

    # Sentence 2: signed sensitivity of the exposed portion.
    b = grab(r"signed sensitivity(?: of)?\s+{N}", text)

    # Sentence 3: target portfolio value change.
    dV = grab(r"target portfolio value change(?: of)?\s+(?:USD\s+|\$\s*)?{N}", text)

    # Factor-exposed portfolio value (checkpoint 1).
    exposed = V * s

    # Signed factor shock x such that exposed * b * x = dV.
    shock = dV / (exposed * b)

    # Reported as a percentage (sign preserved).
    final = shock * 100

    return {"final": final, "slots": {"exposed_value_checkpoint": exposed}}
