"""h044 -- early vs deferred cleanup NPV difference (literal transcription).

Sentence-by-sentence:
  1. Non-cleanup cash flows are identical -> cancel; only cleanup-related flows matter.
  2. Valuation-date base cleanup estimate C0.
  3. Grows at nominal effective annual escalation rate g; early plan pays
     C0 * (1+g)^T_early at end of year T_early.
  4. Deferred plan pays C0 * (1+g)^T_def at end of year T_def, plus a fixed nominal
     administration outflow A paid only at T_def.
  5. Discount all cleanup-related flows at nominal effective annual rate r, annual compounding.
  6. Same basis; rates are decimal ratios (not percent).
  7. Result = NPV(deferred) - NPV(early); outflows are negative cash flows.
Checkpoints:
  early_cleanup_growth_factor_checkpoint = (1+g)^T_early
  terminal_discount_factor_checkpoint    = 1 / (1+r)^T_def
"""

from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "h044"


def _pow(base: Fraction, exponent: Fraction) -> Fraction:
    exponent = Fraction(exponent)
    if exponent.denominator == 1:
        return Fraction(base) ** int(exponent)
    return real_pow(Fraction(base), exponent)


def solve(text: str, q: dict) -> dict:
    # Sentence 2: base cleanup estimate at the valuation date.
    base_estimate = grab(r"base cleanup estimate is {N}", text)
    # Sentence 3: escalation rate (decimal ratio) and the early payment date.
    escalation_rate = grab(r"escalation rate {N}", text)
    early_year = grab(r"early plan pays the resulting cleanup cost at the end of year {N}", text)
    # Sentence 4: deferred payment date and administration outflow at that terminal date.
    deferred_year = grab(r"deferred plan pays the resulting cleanup cost at the end of year {N}", text)
    admin_outflow = grab(r"administration outflow of {N}", text)
    # Sentence 5: discount rate (decimal ratio), annual compounding.
    discount_rate = grab(r"Discount all cleanup-related cash flows at the nominal effective annual rate {N}", text)

    one = Fraction(1)

    # Early plan: escalated cleanup cost paid at end of early_year.
    early_growth_factor = _pow(one + escalation_rate, early_year)
    early_cleanup_cost = base_estimate * early_growth_factor
    early_discount_factor = one / _pow(one + discount_rate, early_year)
    npv_early = -early_cleanup_cost * early_discount_factor

    # Deferred plan: escalated cleanup cost plus admin outflow at end of deferred_year.
    deferred_growth_factor = _pow(one + escalation_rate, deferred_year)
    deferred_cleanup_cost = base_estimate * deferred_growth_factor
    terminal_discount_factor = one / _pow(one + discount_rate, deferred_year)
    npv_deferred = -(deferred_cleanup_cost + admin_outflow) * terminal_discount_factor

    # Sentence 7: NPV(deferred) minus NPV(early), signed.
    difference = npv_deferred - npv_early

    return {
        "final": difference,
        "slots": {
            "early_cleanup_growth_factor_checkpoint": early_growth_factor,
            "terminal_discount_factor_checkpoint": terminal_discount_factor,
        },
    }
