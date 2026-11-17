"""h074 -- two-tranche (green / conventional) compound maturity repayment, solve for principal.

AMBIGUITY HUNT (resolutions with textual evidence):

1. Share unit. "The green tranche receives share 0.7" / "share 11/21": a plain ratio of the
   total principal, not a percent. Conventional share = 1 - green share, because "The remaining
   principal funds the conventional tranche". (Robustness: if a future instance writes
   "share 70 percent" we divide by 100; if it states an explicit conventional share we use it.)

2. Yield unit. "earns annual yield ratio 0.05": a ratio, used directly (0.05, not 0.05/100).
   (Robustness: "yield 5 percent" -> /100.)

3. Compounding. "compounds for 5 annual periods" with an "annual yield" -> annual compounding,
   factor = (1 + r) ** n, exact Fraction integer power. Not simple interest. Each tranche has its
   own n (instances 2 and 3 have different n for the two tranches), so the two factors are
   computed independently -- never a shared horizon.

4. What "green principal share multiplied by its compound maturity factor" means. If it meant the
   bare share (0.7) times the factor, the repayment would be a constant ~1.38 that can never equal a
   cap of 124.48, so the "green principal share" is the green principal amount P * s. Hence
   repayment(P) = P * (s * F_g + (1 - s) * F_c).

5. "maximum total principal that makes repayment exactly equal to the cap". Repayment is strictly
   increasing and linear in P, so the equation has exactly one solution; "maximum" is a red
   herring. P = cap / (s * F_g + (1 - s) * F_c). No rounding inside (no whole-unit language).

6. Checkpoint "full-term compound factor for the green-bond tranche" (unit "multiple") is F_g =
   (1 + r_g) ** n_g by itself -- NOT multiplied by the share, NOT by the principal, NOT the
   blended factor. "Full-term" = over all n_g periods.

7. Units: cap is in USD (answer_spec unit usd), so P is in USD; returned unrounded, the framework
   rounds half-up to 2 dp. Checkpoint returned unrounded (framework rounds to 8 dp).

PARSING NOTES: the green values and the conventional values live in different sentences, so every
lazy "reach" is bounded at a sentence end (a '.' followed by whitespace / end of text), which lets
it cross decimal points inside numbers such as 0.05 but never leak into the other tranche's
sentence. NUMBER contains a top-level '|' so it is always wrapped in a group when inlined.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, real_pow

TEMPLATE_ID = "h074"

_NUM = f"(?:{NUMBER})"
_PCT = r"\s*(?:percent|%)"
# Lazy filler that may cross decimal points but never a sentence boundary.
_SENT = r"(?:(?!\.(?:\s|$))[\s\S])*?"


def _num(pattern: str, text: str) -> tuple[Fraction, bool]:
    """Search ``pattern`` (exactly one {N}); return (value, followed_by_percent)."""
    rx = pattern.replace("{N}", f"({NUMBER})") + f"({_PCT})?"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return F(m.group(1)), bool(m.group(2))


def _ratio(pattern: str, text: str) -> Fraction:
    """A share / yield stated as a ratio (default) or as a percent (then /100)."""
    val, is_pct = _num(pattern, text)
    return val / 100 if is_pct else val


def _count(pattern: str, text: str) -> Fraction:
    val, _ = _num(pattern, text)
    return val


def _factor(rate: Fraction, n: Fraction) -> Fraction:
    base = 1 + rate
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)  # only if a non-integer period count ever appears


_GREEN = r"green(?:-bond)?\s+tranche"
_CONV = r"conventional\s+tranche"
_YIELD = r"earns\s+(?:an?\s+)?annual\s+yield\s+(?:ratio\s+|rate\s+|of\s+)?{N}"
_PERIODS = r"compounds\s+(?:annually\s+)?for\s+{N}\s+annual\s+periods?"


def solve(text: str, q: dict) -> dict:
    # --- green tranche -------------------------------------------------------------------
    s_green = _ratio(_GREEN + _SENT + r"share\s+(?:of\s+)?{N}", text)
    r_green = _ratio(_GREEN + _SENT + _YIELD, text)
    n_green = _count(_GREEN + _SENT + _PERIODS, text)

    # --- conventional tranche ------------------------------------------------------------
    r_conv = _ratio(_CONV + _SENT + _YIELD, text)
    n_conv = _count(_CONV + _SENT + _PERIODS, text)

    # Conventional share: "The remaining principal funds the conventional tranche" -> 1 - s_green.
    # Robustness only: honour an explicit conventional share if one is ever stated.
    if re.search(_CONV + r"\s+receives\s+(?:a\s+)?share", text, flags=re.I):
        s_conv = _ratio(_CONV + r"\s+receives\s+(?:a\s+)?share\s+(?:of\s+)?{N}", text)
    else:
        s_conv = 1 - s_green

    # --- cap -----------------------------------------------------------------------------
    cap = _count(r"maturity[- ]repayment\s+cap\s+(?:of\s+)?(?:USD\s+)?{N}", text)

    # --- compute -------------------------------------------------------------------------
    f_green = _factor(r_green, n_green)
    f_conv = _factor(r_conv, n_conv)

    blended = s_green * f_green + s_conv * f_conv  # repayment per 1 unit of total principal
    principal = cap / blended

    return {
        "final": principal,
        "slots": {"green_maturity_factor_checkpoint": f_green},
    }
