"""Cluster h056 -- two-factor stress loss with an interaction term, a concentration
add-on, and a floor at an external stress loss.

Text (instance 1):
  "A portfolio worth 99 has factor shock ratios 0.05 and 0.2, with respective loss
   sensitivities 0.2 and 0.2. Their joint effect is the product of both shocks and
   0.01. A concentration ratio 0.1 adds its squared value to the modeled loss rate.
   Compute the modeled loss from the sum of both linear factor rates, the joint rate,
   and the concentration square. The required capital charge is the larger of that
   modeled loss and external stress loss 3."

Final answer: capital charge, unit usd, half-up 2 dp.
Checkpoint joint_ratio_checkpoint: "the joint interaction loss ratio", unit ratio, 6 dp.

AMBIGUITIES CONSIDERED AND HOW EACH WAS RESOLVED
------------------------------------------------
A1  "linear factor rates".  Resolved: rate_i = shock_i * sensitivity_i, paired by
    position.  Evidence: "factor shock ratios a and b, with RESPECTIVE loss
    sensitivities c and d" -- 'respective' pairs first with first, second with second,
    and a loss RATE arising from a shock is the shock scaled by its loss sensitivity.
    (Neither the shock alone nor the sensitivity alone is a 'linear factor rate'.)

A2  "Their joint effect is the product of both shocks and k".  Resolved:
    joint_rate = shock_1 * shock_2 * k.  'both shocks' are the two "factor shock
    ratios" -- the quantity the sentence calls shocks.  The sensitivities are a
    separately named quantity and are NOT folded in; nor is the product taken over
    the two linear rates.  'and k' extends the product (a three-way product), it is
    not an addition.

A3  Checkpoint "joint interaction loss ratio" (unit ratio).  Resolved: it is the joint
    RATE from A2 itself (dimensionless), not the joint loss in USD (V * joint rate).
    Evidence: result unit 'ratio'; the body calls the same quantity "the joint rate".

A4  Concentration.  Resolved: c**2 is added at the RATE level.  Evidence: "adds its
    squared value to the modeled loss RATE", and the summation sentence lists "the
    concentration square" alongside the other rates.  It is not added in USD.

A5  Modeled loss (USD) = portfolio value * (rate_1 + rate_2 + joint_rate + c**2).
    Evidence: final unit is usd; the portfolio is "worth V"; the text speaks of a
    "modeled loss rate", so the loss is that rate applied to the portfolio value.

A6  "external stress loss S".  Resolved: S is a USD amount, compared directly with the
    modeled loss in USD.  Evidence: every genuine ratio in the text is a decimal below
    1 (0.05, 0.2, 0.1, 0.01), whereas S is 3 / 5.4 / 5 against a portfolio of ~100 --
    a USD loss, not a rate; and the capital charge (usd) is "the larger of that
    modeled loss and" S, so both operands must be in USD.  Not a percent.

A7  "the larger of" -> max(modeled_loss, S).  A tie returns the common value, so no
    tie-break rule is needed.  No floor at zero is stated (and none is reachable with
    non-negative inputs), so none is applied.

A8  Rounding: nothing in the text says any intermediate is rounded or truncated, so
    everything is exact Fractions; the framework rounds the final (2 dp) and the
    checkpoint (6 dp) independently.

A9  Units of the ratios: all shocks/sensitivities/coefficients are already plain
    decimals (no 'percent'), so no /100 conversion.  Defensively, a number followed
    by 'percent' or '%' is divided by 100 if that wording ever appears.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h056"

_PCT_TAIL = r"\s*(?:percent|per cent|%)"


def _num(pattern: str, text: str, pct_ok: bool = True) -> Fraction:
    """Grab the single {N} in ``pattern``; divide by 100 if 'percent'/'%' follows it."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if pct_ok and re.match(_PCT_TAIL, text[m.end(1):], flags=re.I):
        v /= 100
    return v


def _pair(pattern: str, text: str) -> tuple[Fraction, Fraction]:
    """Grab two {N} captures (e.g. 'ratios {N} and {N}'), percent-aware for each."""
    # Each number may carry its own optional 'percent'/'%' tail (e.g. "5 percent and 20%").
    rx = pattern.replace("{N}", f"({NUMBER})(?:{_PCT_TAIL})?")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    out = []
    for g in (1, 2):
        v = F(m.group(g))
        if re.match(_PCT_TAIL, text[m.end(g):], flags=re.I):
            v /= 100
        out.append(v)
    return out[0], out[1]


def solve(text: str, q: dict) -> dict:
    body = text or q.get("question", "")

    # Portfolio value (USD).
    V = _num(r"portfolio\s+(?:is\s+)?worth\s+(?:USD\s*|\$\s*)?{N}", body, pct_ok=False)

    # Factor shocks and their respective loss sensitivities (A1).
    s1, s2 = _pair(r"factor\s+shock\s+ratios?\s+(?:of\s+)?{N}\s+and\s+{N}", body)
    b1, b2 = _pair(r"loss\s+sensitivit(?:y|ies)\s+(?:of\s+)?{N}\s+and\s+{N}", body)

    # Interaction coefficient (A2): "product of both shocks and k".
    k = _num(r"product\s+of\s+(?:both|the\s+two)\s+shocks?\s+and\s+{N}", body)

    # Concentration ratio (A4).
    c = _num(r"concentration\s+ratio\s+(?:of\s+)?{N}", body)

    # External stress loss, in USD (A6).
    S = _num(r"external\s+stress\s+loss\s+(?:of\s+)?(?:USD\s*|\$\s*)?{N}", body, pct_ok=False)

    # Linear factor rates (A1).
    r1 = s1 * b1
    r2 = s2 * b2

    # Joint interaction rate (A2) -- this is the checkpoint quantity (A3).
    joint_rate = s1 * s2 * k

    # Concentration square (A4).
    conc_sq = c * c

    # Modeled loss rate and modeled loss in USD (A5).
    loss_rate = r1 + r2 + joint_rate + conc_sq
    modeled_loss = V * loss_rate

    # Capital charge: the larger of modeled loss and the external stress loss (A7).
    charge = max(modeled_loss, S)

    return {
        "final": charge,
        "slots": {"joint_ratio_checkpoint": joint_rate},
    }
