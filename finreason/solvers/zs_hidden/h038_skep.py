"""h038 -- tax-loss harvest vs no-harvest terminal wealth advantage.

Structure (all three instances share it, only numbers differ):
  L   = fully usable eligible loss magnitude (USD)
  t   = current-year tax rate (ratio)
  R   = immediate tax reduction = L * t                     <- checkpoint 1 (USD)
  P   = original principal (USD)
  r_i = intended annual effective total-return rate (ratio)
  s   = additive annual tracking shortfall (ratio)
  n   = years of annual compounding
  harvest path    : (P + R) * (1 + r_i - s) ** n
  no-harvest path : P * (1 + r_i) ** n
  final           : harvest - no_harvest   (signed, USD)

AMBIGUITIES CONSIDERED AND HOW THE TEXT RESOLVES THEM
1. Tax rate "0.5": ratio or percent?  The text never says "percent"/"%"; the intended
   rate (0.5) and shortfall (0.25) use the same bare-decimal convention and are combined
   additively ("0.5 minus ... 0.25"), so all three are plain ratios.  A 0.5 % tax rate
   or a 0.5 % return would also make the "positive result means the invested tax
   reduction exceeds the cumulative tracking shortfall" framing meaningless.  Defensive:
   if a "percent"/"%" token follows any rate number we divide by 100.
2. Replacement rate: ADDITIVE subtraction r_i - s (text: "intended rate ... minus the
   ADDITIVE annual tracking shortfall"), not multiplicative (1+r_i)(1-s) and not a
   fee on the balance.
3. What earns the replacement rate: the WHOLE harvest-path investment, i.e. original
   principal PLUS the tax reduction ("invests the original ... principal plus that tax
   reduction in a permitted replacement exposure. The replacement earns ...").
4. No-harvest path: the original principal only, at the intended rate, no tax reduction
   ("same original principal remains in the intended exposure and no tax reduction is
   received").
5. Sign: final = harvest - no_harvest ("signed terminal wealth advantage of the
   tax-harvest path over the no-harvest path"); no floor at zero, may be negative.
6. Rounding inside the chain: none.  "Use exact arithmetic" -- the tax reduction is
   NOT rounded to cents before being invested; the checkpoint is returned unrounded
   (the framework applies half-up 4 dp).
7. Compounding: "annual effective total-return rate" compounded "annually for n years
   with dividends reinvested and no intermediate cash flow" -> growth factor (1+r)**n,
   integer power, exact.  If n were ever non-integer we fall back to real_pow.
8. No terminal taxation, fees, wash-sale, or offset limits ("ignore ... future basis-tax
   consequences"), so terminal wealth is pre-tax on both paths.
9. Tax reduction timing: "available at time 0" and "invested at time zero" -> it
   compounds for the full n years alongside the principal (no partial-year adjustment).
10. "loss magnitude" is a positive magnitude; R = L * t is a positive reduction.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, real_pow

TEMPLATE_ID = "h038"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate anchored by ``pattern`` (which contains {N}); convert percent -> ratio
    only if the number is explicitly followed by a percent token."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    tail = text[m.end(1) : m.end(1) + 12]
    if re.match(r"\s*(?:percent|%|pct)\b", tail) or re.match(r"\s*%", tail):
        value /= 100
    return value


def _first(patterns: list[str], text: str, use_rate: bool = False) -> Fraction:
    last_err: Exception | None = None
    for p in patterns:
        try:
            return _rate(p, text) if use_rate else grab(p, text)
        except ValueError as exc:  # pattern not found -> try next anchor
            last_err = exc
    raise ValueError(f"none of {patterns!r} matched") from last_err


def solve(text: str, q: dict) -> dict:
    # --- loss magnitude (USD)
    loss = _first(
        [
            r"loss magnitude of (?:USD\s*)?{N}",
            r"loss (?:magnitude )?of (?:USD\s*)?{N}",
            r"loss magnitude[^.0-9-]*{N}",
        ],
        text,
    )
    # --- current-year tax rate (ratio; percent handled defensively)
    tax_rate = _first(
        [
            r"tax rate (?:is|of|equals)\s*{N}",
            r"tax rate[^.0-9-]*{N}",
        ],
        text,
        use_rate=True,
    )
    # --- original principal (USD)
    principal = _first(
        [
            r"original (?:USD\s*)?{N}\s*(?:USD\s*)?principal",
            r"original principal of (?:USD\s*)?{N}",
            r"principal of (?:USD\s*)?{N}",
            r"principal[^.0-9-]*{N}",
        ],
        text,
    )
    # --- intended annual effective rate (ratio)
    intended = _first(
        [
            r"intended rate (?:of\s*)?{N}",
            r"intended (?:annual )?(?:effective )?(?:total-return )?rate[^.0-9-]*{N}",
        ],
        text,
        use_rate=True,
    )
    # --- additive annual tracking shortfall (ratio)
    shortfall = _first(
        [
            r"tracking shortfall (?:of\s*)?{N}",
            r"shortfall[^.0-9-]*{N}",
        ],
        text,
        use_rate=True,
    )
    # --- horizon in years (annual compounding)
    years = _first(
        [
            r"(?:for|over)\s*{N}\s*years?",
            r"{N}\s*years?",
        ],
        text,
    )

    # Checkpoint: immediate current-year tax reduction invested at time zero (USD).
    tax_reduction = loss * tax_rate

    replacement_rate = intended - shortfall  # additive shortfall
    harvest_start = principal + tax_reduction

    def grow(amount: Fraction, rate: Fraction) -> Fraction:
        base = 1 + rate
        if years.denominator == 1:
            return amount * base ** int(years)
        return amount * real_pow(base, years)

    harvest_terminal = grow(harvest_start, replacement_rate)
    no_harvest_terminal = grow(principal, intended)

    advantage = harvest_terminal - no_harvest_terminal  # signed, USD

    return {
        "final": advantage,
        "slots": {"immediate_tax_reduction_checkpoint": tax_reduction},
    }
