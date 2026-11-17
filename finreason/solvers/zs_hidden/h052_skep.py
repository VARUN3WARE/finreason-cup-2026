"""h052 -- sustainability report: waste-cost reduction rate needed to hit a combined savings target.

Structure (all three instances):
    annual energy expenditure E, achieved energy-reduction ratio r,
    annual waste-management expenditure W, combined annual savings target T.
    energy_savings = E * r                      (checkpoint, usd)
    waste_savings_needed = T - energy_savings
    waste rate x = waste_savings_needed / W     (final, percent -> x * 100)

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED
A1  "energy-reduction ratio 0.2" -- ratio or percent?  RATIO (plain fraction, 0.2 = 20%).
    Evidence: the text calls it a "ratio", and deliberately contrasts it with the answer which is to be
    "expressed as a percentage".  Robustness: if a variant writes "X percent"/"X%" the parser divides by 100.
A2  Base of the energy savings -- energy expenditure E only, not the combined (E + W) spend.
    Evidence: the slot is "savings contributed by energy reduction", and the ratio is explicitly the
    *energy*-reduction ratio paired with the *energy* expenditure sentence.
A3  "combined annual savings target" -- an absolute USD amount (= energy savings + waste savings), not a
    fraction of total spend.  Evidence: the checkpoint unit is usd; T (e.g. 148.85) is the same scale as the
    expenditures and would be a nonsensical ratio (>1 is impossible, and 148.85/692 is not a stated target).
A4  Base of the waste-cost reduction rate -- waste-management expenditure W only (waste savings = W * x).
    Evidence: "waste-cost reduction rate" parallels "energy-reduction ratio" which applies to energy spend;
    a reduction *rate of waste cost* is by definition relative to the waste cost.
A5  Final unit -- "expressed as a percentage" and answer_spec unit "percent": return x * 100 (25.09 = 25.09%).
A6  Rounding -- none inside the chain.  "round only the final value"; the checkpoint E*r is returned exact
    (the framework rounds half-up to 2 dp).  NB instance 1 gives exactly 97.415, a half-up boundary -> 97.42;
    exact Fractions guarantee this where floats would not.
A7  Floors / caps -- none are worded (no "at least zero", no "capped at 100%"), so the sign of
    (T - E*r)/W is preserved as-is.  All three instances fall strictly inside (0, 1) anyway.
A8  Periods -- every quantity is annual; no per-period conversion.
A9  "the rate that must be reported" -- a plain request for the value; it does not introduce reporting
    rounding before the final step.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h052"


def _ratio(text: str) -> Fraction:
    """Achieved energy-reduction ratio as a plain fraction (handles a 'percent'/'%' variant)."""
    m = re.search(
        r"energy[- ]reduction (?:ratio|rate|fraction)(?: of| is|:)?\s*(" + NUMBER + r")\s*(percent|%)?",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        raise ValueError("energy-reduction ratio not found")
    r = F(m.group(1))
    if m.group(2):
        r /= 100
    return r


def solve(text: str, q: dict) -> dict:
    # (?i): sentence-initial capitals ("Annual waste-...") must not break the word anchors.
    energy_exp = grab(r"(?i)(?:annual )?energy expenditure(?: of| is|:)?\s*{N}", text)
    r = _ratio(text)
    waste_exp = grab(r"(?i)waste[- ]management expenditure(?: of| is|:)?\s*{N}", text)
    target = grab(r"(?i)(?:combined )?(?:annual )?savings target(?: of| is|:)?\s*{N}", text)

    energy_savings = energy_exp * r              # USD saved by the achieved energy reduction
    waste_savings_needed = target - energy_savings
    waste_rate = waste_savings_needed / waste_exp  # plain ratio of waste expenditure

    return {
        "final": waste_rate * 100,               # percent
        "slots": {"energy_savings_checkpoint": energy_savings},
    }
