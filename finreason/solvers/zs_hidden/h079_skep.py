"""Solver for hidden cluster h079 -- minimum reported EBITDA to support a target equity value.

Chain (all values implicitly in USD million, no unit conversions anywhere):
    net_debt            = total_debt - cash
    enterprise_value    = target_equity_value + net_debt
    normalized_ebitda   = enterprise_value / ev_ebitda_multiple
    reported_ebitda     = normalized_ebitda + recurring_deduction        <- final answer

AMBIGUITIES CONSIDERED AND HOW EACH WAS RESOLVED (textual evidence in quotes):

A1. Net-debt sign when cash exceeds debt (instance t1_i6ihctgkcoskhtlhirkti: debt 9, cash 29).
    "total debt ... and cash ..., which are the only enterprise-value-to-equity-value adjustments"
    -> Equity = EV - Debt + Cash, hence EV = Equity + (Debt - Cash). Nothing in the text floors net
    debt at zero or says "net cash is ignored", so net debt is signed: -20 in that instance, and the
    checkpoint reports the signed value (-20.0000). Instance 3 has debt == cash -> net debt exactly 0.

A2. "the buyer values normalized EBITDA at 6" -- multiple or dollar amount?
    The task then says "infer required normalized EBITDA", which is only a meaningful inference step if
    6 is an EV/EBITDA valuation multiple (EV = 6 x normalized EBITDA). If 6 were the EBITDA itself there
    would be nothing to infer. -> normalized EBITDA = EV / multiple. Division is exact (Fraction).

A3. Deduction: absolute amount vs percentage.
    "a recurring EBITDA deduction of 0.01 from the reported figure" -- no "percent"/"%" wording, and
    every other figure is an unlabelled usd_million amount, so the deduction is an absolute USD-million
    amount. normalized = reported - deduction, so "restore the deduction" means reported = normalized
    + deduction (add it back, never subtract, never scale).

A4. "minimum reported EBITDA required to support the target equity price".
    With a fixed multiple the relation is monotone, so the minimum is the equality solution; no
    whole-unit / ceiling rounding is mentioned, so the exact rational value is returned and the
    framework applies half-up to 2 dp. Likewise the checkpoint is returned unrounded (4 dp half-up is
    applied by the framework) and the rendered checkpoint is never fed back into the chain.

A5. Direction of the bridge. "first bridge equity value to enterprise value using net debt":
    EV = Equity + Net debt (the standard identity Equity = EV - Net debt rearranged). The multiple is
    applied to the *enterprise* value (an EV/EBITDA multiple), not to equity value.

A6. Checkpoint identity. net_debt_checkpoint = "Compute net debt for the equity-to-enterprise bridge"
    -> debt - cash, in usd_million, position 1 (before the EV bridge). Not EV, not the adjustment to
    equity with reversed sign.

Parsing is anchored on surrounding words; nothing is hard-coded per instance.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h079"


def _grab_any(patterns: list[str], text: str) -> Fraction:
    """Try several anchored patterns in order; first hit wins. Case-insensitive."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is not None:
            return F(m.group(1))
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    # --- inputs -------------------------------------------------------------------------------
    equity_value = _grab_any(
        [
            r"target equity value of\s*(?:USD\s*)?{N}",
            r"equity value of\s*(?:USD\s*)?{N}",
            r"equity price of\s*(?:USD\s*)?{N}",
        ],
        text,
    )
    total_debt = _grab_any(
        [
            r"total debt of\s*(?:USD\s*)?{N}",
            r"\bdebt of\s*(?:USD\s*)?{N}",
        ],
        text,
    )
    cash = _grab_any(
        [
            r"\bcash (?:and equivalents )?of\s*(?:USD\s*)?{N}",
            r"\bcash of\s*(?:USD\s*)?{N}",
        ],
        text,
    )
    multiple = _grab_any(
        [
            r"values normali[sz]ed EBITDA at\s*{N}",
            r"normali[sz]ed EBITDA (?:multiple|at)\s*(?:of\s*)?{N}",
            r"EBITDA multiple of\s*{N}",
        ],
        text,
    )
    deduction = _grab_any(
        [
            r"EBITDA deduction of\s*(?:USD\s*)?{N}",
            r"deduction of\s*(?:USD\s*)?{N}",
        ],
        text,
    )

    # --- chain (exact rational arithmetic) ----------------------------------------------------
    # A1/A6: signed net debt, no floor.
    net_debt = total_debt - cash
    # A5: equity -> enterprise bridge.
    enterprise_value = equity_value + net_debt
    # A2: the multiple is an EV / normalized-EBITDA multiple.
    normalized_ebitda = enterprise_value / multiple
    # A3: normalized = reported - deduction  =>  reported = normalized + deduction.
    reported_ebitda = normalized_ebitda + deduction

    return {
        "final": reported_ebitda,
        "slots": {"net_debt_checkpoint": net_debt},
    }
