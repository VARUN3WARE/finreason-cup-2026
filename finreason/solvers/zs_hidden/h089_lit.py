"""h089 -- fictional KYC control-credit policy: minimum additional verified-control credit.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h089"


def solve(text: str, q: dict) -> dict:
    # "A customer has source-of-funds risk score S, jurisdiction risk score J,
    #  existing verified-control credit E, and standard residual-risk ceiling C."
    source_of_funds = grab(r"source-of-funds risk score {N}", text)
    jurisdiction = grab(r"jurisdiction risk score {N}", text)
    existing_credit = grab(r"existing verified-control credit {N}", text)
    ceiling = grab(r"residual-risk ceiling {N}", text)

    # "All four values use the same additive risk-point scale." -> add/subtract directly.

    # Checkpoint: "the source-of-funds score plus the jurisdiction score"
    combined_risk = source_of_funds + jurisdiction

    # "Existing and additional verified-control credit each reduce residual risk one-for-one"
    # residual = combined - existing - additional ; require residual <= ceiling
    # => additional >= combined - existing - ceiling
    # "additional credit cannot be negative" -> floor at zero; minimum is the max of the two.
    required_unfloored = combined_risk - existing_credit - ceiling
    additional_credit = max(Fraction(0), required_unfloored)

    # sanity: the constraint is satisfied (no greater than = <=)
    assert combined_risk - existing_credit - additional_credit <= ceiling

    return {
        "final": additional_credit,
        "slots": {"combined_risk_checkpoint": combined_risk},
    }
