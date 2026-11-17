# FINANCE MODEL (h030): fictional remediation budget with a self-reporting credit.
#
#   base          = base assessment (USD)
#   delay_charge  = delay_days * per_day_rate           (USD; simple linear charge, no compounding)
#   combined      = base + delay_charge                 (the "combined assessment and delay charge")
#   credit        = fractional credit rate (already a plain fraction, NOT percent; e.g. 0.2999995)
#   retained      = 1 - credit                          (slot: post_credit_factor_checkpoint, ratio, 6 dp half-up)
#   credited      = combined * retained                 (credit applies to base + delay charge only)
#   monitoring    = mandatory monitoring cost (USD), added AFTER the credit, "outside the credit base"
#   total         = credited + monitoring               (final answer, USD, 2 dp half-up)
#
# Conventions / overrides:
#   - The credit rate is given as a fraction (0.27 = 27%), not percent; the text says "retained fraction is one minus that rate".
#   - No rounding inside the chain: checkpoint and final are rounded independently by the framework from exact values.
#   - Monitoring cost is NOT reduced by the credit.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h030"


def solve(text: str, q: dict) -> dict:
    base = grab(r"base assessment {N} USD", text)
    days, per_day = grab_all(r"reporting delay of {N} days incurs {N} USD per day", text)
    credit = grab(r"Treat {N} as the fractional credit", text)
    monitoring = grab(r"mandatory monitoring cost {N} USD", text)

    delay_charge = days * per_day
    combined = base + delay_charge
    retained = 1 - credit
    total = combined * retained + monitoring

    return {"final": total, "slots": {"post_credit_factor_checkpoint": retained}}
