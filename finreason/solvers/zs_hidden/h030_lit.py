"""h030 -- fictional remediation budget: (base + delay charge) * retained fraction + monitoring.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h030"


def solve(text: str, q: dict) -> dict:
    # "Begin with base assessment {B} USD."
    base_assessment = grab(r"base assessment {N} USD", text)

    # "A reporting delay of {D} days incurs {R} USD per day."
    delay_days = grab(r"reporting delay of {N} days?", text)
    delay_rate_per_day = grab(r"incurs {N} USD per day", text)
    delay_charge = delay_days * delay_rate_per_day

    # "Treat {c} as the fractional credit applied to the combined assessment and
    #  delay charge, so the retained fraction is one minus that rate."
    credit_rate = grab(r"Treat {N} as the fractional credit", text)
    combined_assessment = base_assessment + delay_charge
    retained_fraction = Fraction(1) - credit_rate
    credited_amount = combined_assessment * retained_fraction

    # "Then add mandatory monitoring cost {M} USD outside the credit base."
    monitoring_cost = grab(r"monitoring cost {N} USD", text)

    total_remediation_budget = credited_amount + monitoring_cost

    return {
        "final": total_remediation_budget,
        "slots": {"post_credit_factor_checkpoint": retained_fraction},
    }
