"""h091 -- QoE-adjusted EBITDA, customer-attrition EV scenario vs. insured tax exposure.

Chain (per instance text):
    adjusted EBITDA        = verified recurring EBITDA + confirmed run-rate savings
    base-case EV           = adjusted EBITDA * base multiple
    attrition-case EBITDA  = adjusted EBITDA - attrition fall            [slot attrition_case_ebitda_checkpoint]
    attrition-case EV      = attrition-case EBITDA * compressed multiple
    expected customer loss = P(attrition) * (base-case EV - attrition-case EV)
    uninsured exposure     = gross tax exposure * (1 - insurance recovery fraction)   [slot uninsured_tax_exposure_checkpoint]
    expected tax loss      = P(crystallization) * uninsured exposure
    final                  = exact comparison of the two unrounded expected losses

AMBIGUITY HUNT -- points where two analysts could disagree, and how each was resolved:

A1. Are the run-rate savings part of the valuation EBITDA, or a distractor?
    Text: "target-controlled confirmed run-rate savings NOT ALREADY INCLUDED in that amount".
    "target-controlled" + "confirmed" are exactly the QoE criteria for a creditable run-rate
    adjustment, and "not already included" exists to prevent double counting, i.e. it tells the
    reader to ADD them.  A distractor would be worded "buyer-dependent"/"unconfirmed".
    => savings are added to the verified figure in BOTH states (they are cost savings the target
    controls; customer attrition does not remove them).  Base EV = (E + S) * M.

A2. What does "recurring EBITDA falls by D" fall FROM, and what does the slot
    "attrition_case_ebitda" denote?  Candidates: (E + S) - D (adjusted basis in the attrition
    state) or E - D (verified figure only, savings re-added later).  Both give the SAME attrition
    EV ((E + S - D) * m), so the final answer is unaffected; only the checkpoint differs.
    Resolution: the slot id "attrition_case_ebitda" parallels the text's "attrition-case
    enterprise value", i.e. it is the EBITDA that is multiplied by the compressed multiple to get
    that EV.  "not already included in that amount" says the savings BELONG in the recurring
    EBITDA measure, so the complete recurring EBITDA is E + S and it falls to E + S - D.
    (In all three instances D == S, so the attrition-case EBITDA equals the verified figure --
    consistent with a deliberate design "attrition erases the run-rate uplift".)
    => checkpoint 1 = E + S - D.

A3. Is "falls by D" absolute or percent?  No "percent"/"%" anywhere; D carries the same bare
    units as E and S and the slot unit is usd_million.  => absolute (USD million).

A4. "valuation multiple compresses TO m" (not "by") => attrition multiple = m exactly.

A5. Direction/sign of the EV difference: "difference between base-case and attrition-case
    enterprise values" => base EV - attrition EV (a loss); no floor at zero is stated, so none
    is applied (it is positive in every instance anyway).

A6. "insurance recovers fraction r" => r is a plain fraction (0.2 = 20%), not a percent;
    uninsured exposure = G * (1 - r).  Recovery is conditional on crystallization, so the
    expected tax loss = q * G * (1 - r), exactly as "crystallization probability times the
    uninsured exposure" defines it.  Checkpoint 2 = G * (1 - r) (unweighted by probability,
    per its description "exposure remaining after insurance recovery").

A7. Probabilities are given as plain decimals (0.2, 0.5): used as-is, no /100.

A8. Comparison: "Compare the two exact unrounded expected losses" => exact Fraction comparison,
    strict > / < with the explicit "Expected losses are equal" token on an exact tie.
    No rounding anywhere inside the chain; the framework rounds the slots (half_up, 4 dp).

A9. Units: every monetary figure is a bare number in USD million; slots are usd_million, so the
    unrounded Fractions are returned directly.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h091"

LARGER_CUSTOMER = "Customer attrition loss is larger"
LARGER_TAX = "Tax exposure loss is larger"
EQUAL = "Expected losses are equal"


def solve(text: str, q: dict) -> dict:
    # --- inputs (anchored on surrounding words) ---
    verified_ebitda = grab(r"verified recurring EBITDA is {N}", text)
    run_rate_savings = grab(r"run-rate savings not already included in that amount are {N}", text)
    base_multiple = grab(r"base case applies valuation multiple {N}", text)
    attrition_fall = grab(r"recurring EBITDA falls by {N}", text)
    attrition_multiple = grab(r"valuation multiple compresses to {N}", text)
    p_attrition = grab(r"that state occurs with probability {N}", text)
    gross_tax = grab(r"gross tax exposure of {N}", text)
    p_crystallize = grab(r"crystallizes with probability {N}", text)
    recovery_fraction = grab(r"insurance recovers fraction {N}", text)

    # --- customer-attrition side ---
    adjusted_ebitda = verified_ebitda + run_rate_savings          # A1
    base_ev = adjusted_ebitda * base_multiple
    attrition_ebitda = adjusted_ebitda - attrition_fall           # A2, A3
    attrition_ev = attrition_ebitda * attrition_multiple          # A4
    expected_customer_loss = p_attrition * (base_ev - attrition_ev)   # A5, A7

    # --- tax side ---
    uninsured_exposure = gross_tax * (Fraction(1) - recovery_fraction)   # A6
    expected_tax_loss = p_crystallize * uninsured_exposure

    # --- exact comparison ---  A8
    if expected_customer_loss > expected_tax_loss:
        final = LARGER_CUSTOMER
    elif expected_customer_loss < expected_tax_loss:
        final = LARGER_TAX
    else:
        final = EQUAL

    return {
        "final": final,
        "slots": {
            "attrition_case_ebitda_checkpoint": attrition_ebitda,
            "uninsured_tax_exposure_checkpoint": uninsured_exposure,
        },
    }
