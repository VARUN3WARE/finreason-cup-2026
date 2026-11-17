"""h082 -- carbon compliance: fixed abate-then-buy strategy vs credits-only (skeptic / ambiguity-hunting pass).

AMBIGUITIES FOUND AND HOW EACH WAS RESOLVED (textual evidence in quotes)
-----------------------------------------------------------------------
A1. What does "operational availability false" do to the abate-then-buy strategy?
    Text: "whenever internal abatement is available, it uses exactly the smaller of the compliance
    obligation and abatement capacity before buying credits for the residual" and
    "choose the sole feasible strategy when only one is feasible".
    => When abatement is NOT available, no abatement can be performed, so the abate-then-buy
       strategy cannot be executed: it is INFEASIBLE (not silently degraded into credits-only;
       a degraded version would tie with credits-only and the tie rule would then absurdly pick
       "abate_then_buy" with zero abatement).  Abated quantity = 0 in that branch.

A2. Abated quantity when available: "exactly the smaller of the compliance obligation and abatement
    capacity" => abate_qty = min(obligation, capacity); "it does not optimize" => never anything else.

A3. Feasibility of abate-then-buy when available: residual = obligation - abate_qty must be coverable
    by credits: "at most M ton-equivalent credits available" => residual <= M (NON-strict: buying
    exactly M is allowed).  Residual is >= 0 by construction.

A4. Feasibility of credits-only: obligation <= M (non-strict, same "at most" wording).  Capacity and
    availability are irrelevant to credits-only.

A5. Cost of abate-then-buy = fixed cost + variable cost * abate_qty + credit price * residual.
    "Internal abatement has fixed cost ... and variable cost ... per ton" => fixed cost is incurred
    once whenever the abatement route is actually run (availability true); it is not per ton.
    Cost of credits-only = credit price * obligation.  No fixed cost for credits.

A6. Decision rule: "Choose the lower-cost feasible strategy, prefer abate-then-buy on a cost tie"
    => both feasible: abate_cost <= credits_cost -> abate_then_buy, else credits_only.
    "choose the sole feasible strategy when only one is feasible" -> that one.
    "return no_feasible_strategy when neither is feasible" -> no_feasible_strategy.

A7. Checkpoint "variable internal abatement cost" (slot variable_abatement_total_checkpoint, unit usd):
    the VARIABLE component only (variable cost per ton * abated tons), excluding the fixed cost and
    excluding credit purchases.  When abatement is unavailable nothing is abated, so the variable
    abatement cost actually incurred is 0 (see A1).  It is reported unrounded; the framework rounds
    half-up to 2 dp.  (Alternative reading "variable cost * min(obligation, capacity) even when
    unavailable" was rejected: no abatement occurs, so no variable abatement cost is incurred.)

A8. Units: one credit = one ton of CO2e ("Treat one carbon credit as covering one ton of CO2e"), so
    credit counts, obligation and capacity are all in the same tons unit; costs are in USD.
    Everything is exact Fraction arithmetic; no rounding inside the computation (no whole-unit
    rounding is mentioned: quantities are already integers).

A9. Boolean parsing: "operational availability true|false" -- parsed case-insensitively, tolerating
    an optional "is"/"of"/":" between the phrase and the token; also accepts yes/no and
    available/unavailable as synonyms for robustness.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h082"


def _availability(text: str) -> bool:
    m = re.search(
        r"operational availability\s*(?:is|of|:|=)?\s*(true|false|yes|no|available|unavailable|not available)\b",
        text,
        flags=re.I,
    )
    if m is None:
        # Fallback: any true/false token following the word "availability".
        m = re.search(r"availability[^.]*?\b(true|false)\b", text, flags=re.I)
    if m is None:
        raise ValueError("operational availability flag not found")
    tok = m.group(1).lower()
    return tok in ("true", "yes", "available")


def _grab_any(patterns: list[str], text: str) -> Fraction:
    last = None
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError as exc:  # noqa: PERF203
            last = exc
    raise last  # type: ignore[misc]


def solve(text: str, q: dict) -> dict:
    obligation = _grab_any(
        [r"compliance obligation of {N} tons?", r"compliance obligation (?:of|is)?\s*{N}"], text
    )
    capacity = _grab_any(
        [r"internal abatement capacity (?:of |is )?{N} tons?", r"abatement capacity (?:of |is )?{N}"], text
    )
    available = _availability(text)
    fixed_cost = _grab_any([r"fixed cost (?:of )?{N} USD", r"fixed cost (?:of |is )?{N}"], text)
    variable_cost = _grab_any(
        [r"variable cost (?:of )?{N} USD per ton", r"variable cost (?:of |is )?{N}"], text
    )
    credit_price = _grab_any(
        [r"[Cc]arbon credits cost {N} USD per ton", r"credits? cost (?:of |is )?{N}"], text
    )
    credit_cap = _grab_any(
        [r"at most {N} ton-equivalent credits", r"at most {N} (?:ton-equivalent )?credits", r"at most {N}"],
        text,
    )

    # --- abate-then-buy (fixed, non-optimised) ---------------------------------------- (A1, A2)
    if available:
        abate_qty = min(obligation, capacity)
    else:
        abate_qty = Fraction(0)
    variable_abatement_total = variable_cost * abate_qty  # checkpoint (A7)

    residual = obligation - abate_qty
    abate_feasible = available and residual <= credit_cap  # (A1, A3)
    abate_cost = fixed_cost + variable_abatement_total + credit_price * residual  # (A5)

    # --- credits-only ----------------------------------------------------------------- (A4)
    credits_feasible = obligation <= credit_cap
    credits_cost = credit_price * obligation

    # --- decision --------------------------------------------------------------------- (A6)
    if abate_feasible and credits_feasible:
        final = "abate_then_buy" if abate_cost <= credits_cost else "credits_only"
    elif abate_feasible:
        final = "abate_then_buy"
    elif credits_feasible:
        final = "credits_only"
    else:
        final = "no_feasible_strategy"

    return {
        "final": final,
        "slots": {"variable_abatement_total_checkpoint": variable_abatement_total},
    }
