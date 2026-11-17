"""Cluster h033: three-stage token price stress, burn-vs-emission policy choice by market-cap floor.

Structure (identical across the three instances, numbers differ):
    U       units outstanding
    P       current price (USD, may be a rational like 25761/13312)
    d       per-stage downside ratio removed from the price surviving the previous stage
    n = 3   stress stages ("exactly three", and the text itself states "(1 - d)^3")
    B       units removed under the burn policy
    s       treasury support ratio that raises the stressed price ONCE (burn policy only)
    E       units added under the fallback emission policy (no support)
    T       floor: use burn if its market cap is AT LEAST T USD, else emission

    stressed price      = P * (1 - d)^n
    burn market cap     = (U - B) * stressed * (1 + s)
    emission market cap = (U + E) * stressed
    selected cap        = burn cap if burn cap >= T else emission cap

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED
1. Checkpoint "price-retention ratio after one stress stage" (unit: ratio).
   "Retention" = fraction of price that survives one stage = (1 - d), not the removed ratio d and not
   the stage-1 price in USD (unit is "ratio", and the text names the surviving price as
   "current price times (1 - per-stage downside ratio)"). Returned UNROUNDED; the framework applies
   6-dp half-up. Note instance 3 has 1 - 0.2499995 = 0.7500005, where half-up vs half-even differ;
   we never round it ourselves.
2. "the same ratio d is removed from the price surviving the previous stage" -> multiplicative
   compounding, stressed price = P * (1 - d)^3. The text confirms the formula explicitly, so no
   additive/linear reading (P * (1 - 3d)) is possible. Integer power -> Fraction ** 3, exact.
3. "treasury support raises that stressed price once by ratio s" -> stressed * (1 + s), applied
   exactly once, to the stressed (post-three-stage) price, not to the current price and not as an
   additive USD amount ("by ratio"). Support belongs to the burn policy only; emission policy
   explicitly "receives no support".
4. Units: burn removes B units (U - B); emission adds E units (U + E). Stress stages affect price only
   ("the same ratio ... is removed from the price"), never the unit count.
5. Market cap = units * price for the respective policy; "Ignore any other price effects".
6. Floor test: "at least T" -> non-strict, burn_cap >= T. Done on the EXACT burn market cap
   ("Use exact values for the floor test"), never on a rounded value.
7. Instance 1 contains the literal 0.2 twice (downside ratio and support ratio); every number is
   grabbed with a regex anchored on its surrounding words so the two are never confused.
8. Final answer: the selected market cap in USD, returned unrounded (framework rounds half-up to 2 dp).
9. Number of stages: parsed from the explicit exponent "^3" in the text (falls back to the spelled-out
   word, then to 3), never hardcoded blindly.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h033"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _num_stages(text: str) -> int:
    m = re.search(r"\)\s*\^\s*(\d+)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"exactly\s+([a-z]+)\s+sequential\s+stress\s+stages", text, flags=re.I)
    if m and m.group(1).lower() in _WORDS:
        return _WORDS[m.group(1).lower()]
    m = re.search(r"exactly\s+(\d+)\s+sequential\s+stress\s+stages", text, flags=re.I)
    if m:
        return int(m.group(1))
    return 3


def solve(text: str, q: dict) -> dict:
    units = grab(r"has {N} units", text)
    price = grab(r"current price of {N} USD", text)
    d = grab(r"the same ratio {N} is removed from the price", text)
    n = _num_stages(text)
    burn_units = grab(r"burn policy, {N} units are removed", text)
    support = grab(r"raises that stressed price once by ratio {N}", text)
    emit_units = grab(r"emission policy, {N} units are added", text)
    floor = grab(r"market cap is at least {N} USD", text)

    retention = Fraction(1) - d                      # checkpoint: one-stage price retention ratio
    stressed = price * retention ** n                # three-stage stressed price (USD)

    burn_price = stressed * (Fraction(1) + support)  # support applied once to the stressed price
    burn_cap = (units - burn_units) * burn_price

    emit_cap = (units + emit_units) * stressed       # no support under emission

    selected = burn_cap if burn_cap >= floor else emit_cap

    return {
        "final": selected,
        "slots": {"one_stage_price_retention_checkpoint": retention},
    }
