"""Cluster h069 -- retirement-date selection with a compound-growth feasibility buffer.

Structure (all 3 instances share it):
    A saver has P and adds a one-time contribution C today.  The combined amount (P + C)
    earns an annual rate r (given as a DECIMAL ratio, e.g. "earns 0.02 annually").
    An "earlier" retirement in n_e years requires capital R_e; a "later" retirement in
    n_l years requires R_l.  A date is feasible only if projected capital exceeds its
    requirement by at least a buffer B.  Prefer earlier if feasible, else later if
    feasible, else neither.

Checkpoints:
    earlier_growth_factor_checkpoint = (1 + r) ** n_e      (unit "multiple")
    later_growth_factor_checkpoint   = (1 + r) ** n_l      (unit "multiple")

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
A1. Rate unit.  "earns 0.0500005 annually" / "earns 0.0005 annually" / "earns 0.02 annually"
    are bare decimals with no "percent" or "%" -> they are RATIOS (0.02 = 2%).  Reading
    0.0005 as 0.0005% would make the growth factor ~1.000005, which is absurd for a
    retirement-planning problem, and the token "percent" is absent.  For robustness, if a
    hidden variant does say "percent"/"%" right after the number, we divide by 100.

A2. Compounding convention.  "compound growth factor" + "annually" + whole-year horizons
    -> discrete annual compounding, factor = (1+r)**n with an integer exponent.  Exact
    Fraction power, no continuous compounding, no simple interest.

A3. Which principal grows.  "The combined amount earns ... annually" -> (P + C) grows for the
    full horizon; the contribution is made "today" (time zero) so it compounds for all n years.
    Projected capital at a date = (P + C) * (1+r)**n.  Nothing is withdrawn/added later.

A4. Feasibility test (strict vs non-strict).  "feasible only if projected capital exceeds its
    date-specific requirement by at least B" -> margin = projected - R must satisfy
    margin >= B (non-strict, "at least").  B is an absolute money amount (e.g. 4862), not a
    percentage of R.  Since B > 0 in every instance, margin >= B already implies
    projected > R, so the word "exceeds" adds no extra strictness.  If a hidden variant said
    "by more than B" we use a strict comparison instead (detected from the text).

A5. Decision rule.  "Prefer the earlier date whenever it is feasible; otherwise choose the
    later date if feasible."  -> earlier_date if feasible_e, else later_date if feasible_l,
    else neither_date.  No comparison of margins between dates; the earlier date wins
    whenever it is feasible even if the later one has a bigger margin.

A6. "Earlier" / "later" are the TEXTUAL labels, not a chronological sort.  Instance 2 says
    "earlier retirement in 6 years ... later retirement in 1 years": the label and the horizon
    disagree.  The generator evidently drew the two horizons independently and kept its
    variable names, and the slot descriptions/answer tokens refer to those labels
    ("growth factor to the earlier date", token "earlier_date").  We therefore bind
    n_e/R_e to the sentence that says "earlier retirement" and n_l/R_l to the sentence that
    says "later retirement", without re-sorting by years.

A7. Rounding inside the computation.  No sentence says the growth factor, projected capital or
    margin is rounded before use, so everything stays an exact Fraction; the framework rounds
    the two checkpoints to 6 dp half-up at display time only.  (None of the three instances
    is within rounding distance of its threshold anyway.)

A8. Checkpoint identity.  "compound growth factor" is the multiplier (1+r)**n itself (a
    "multiple" > 1), not the growth (factor - 1) and not the projected capital.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab  # exact number parsing helpers

TEMPLATE_ID = "h069"


def _rate(text: str) -> Fraction:
    """Annual rate as a ratio.  Bare decimal -> ratio; explicit percent marker -> /100."""
    m = re.search(r"earns\s+(" + NUMBER + r")\s*(percent|%)?", text, flags=re.S)
    if m is None:
        # fallback wording: "at <r> annually" / "rate of <r>"
        m = re.search(r"(?:rate of|at)\s+(" + NUMBER + r")\s*(percent|%)?", text, flags=re.S)
    if m is None:
        raise ValueError("annual rate not found")
    r = F(m.group(1))
    if m.group(2):
        r = r / 100
    return r


def _horizon_and_requirement(label: str, text: str) -> tuple[int, Fraction]:
    """(years, required capital) for the sentence labelled 'earlier'/'later' retirement."""
    pat = (
        label
        + r"\s+retirement\s+in\s+(" + NUMBER + r")\s+years?\s+requires\s+(?:capital\s+of\s+)?("
        + NUMBER
        + r")"
    )
    m = re.search(pat, text, flags=re.S)
    if m is None:
        raise ValueError(f"{label} retirement sentence not found")
    years = F(m.group(1))
    if years.denominator != 1:
        raise ValueError(f"non-integer horizon {years} for {label} date")
    return int(years), F(m.group(2))


def solve(text: str, q: dict) -> dict:
    # --- principal pieces -------------------------------------------------------------
    have = grab(r"saver has\s+{N}", text)
    contrib = grab(r"one-time contribution of\s+{N}", text)
    combined = have + contrib  # A3

    # --- annual rate (ratio) ------------------------------------------------------------
    r = _rate(text)  # A1

    # --- the two dates, bound by textual label (A6) ---------------------------------------
    n_e, req_e = _horizon_and_requirement("earlier", text)
    n_l, req_l = _horizon_and_requirement("later", text)

    # --- feasibility buffer and comparison mode (A4) ------------------------------------
    buffer = grab(r"by at least\s+{N}", text) if re.search(r"by at least", text) else None
    strict = False
    if buffer is None:
        m = re.search(r"by more than\s+(" + NUMBER + r")", text)
        if m is None:
            raise ValueError("feasibility buffer not found")
        buffer = F(m.group(1))
        strict = True

    # --- growth factors (A2) and projected capital ---------------------------------------
    gf_e = (1 + r) ** n_e
    gf_l = (1 + r) ** n_l
    proj_e = combined * gf_e
    proj_l = combined * gf_l

    def feasible(proj: Fraction, req: Fraction) -> bool:
        margin = proj - req
        return margin > buffer if strict else margin >= buffer

    feas_e = feasible(proj_e, req_e)
    feas_l = feasible(proj_l, req_l)

    # --- decision (A5) --------------------------------------------------------------------
    if feas_e:
        final = "earlier_date"
    elif feas_l:
        final = "later_date"
    else:
        final = "neither_date"

    return {
        "final": final,
        "slots": {
            "earlier_growth_factor_checkpoint": gf_e,
            "later_growth_factor_checkpoint": gf_l,
        },
    }
