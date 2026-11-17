# FINANCE MODEL (payment-processor batch settlement)
#   G   = gross sales before chargebacks (USD), already INCLUDES the charged-back amount (stated explicitly).
#   n   = number of transactions in the batch.
#   r   = proportional processing rate, applied to the full gross sales G (the text says "on those gross sales").
#   c   = flat fee per transaction; aggregate fixed fees = c * n.
#   CB  = chargebacks included in G; fraction f of CB is recovered, so the unrecovered chargeback loss = CB * (1 - f).
#   R   = reserve withheld by the processor.
#
#   variable_fee   = r * G
#   fixed_fee      = c * n
#   unrecovered_cb = CB * (1 - f)
#   net settlement = G - variable_fee - fixed_fee - unrecovered_cb - R
#
# Conventions / overrides:
#   * Gross sales G is the starting amount (chargebacks are already inside it, so they are NOT subtracted twice:
#     only the UNRECOVERED portion is deducted, once).
#   * The proportional fee is on G (gross, before chargebacks), NOT on G net of chargebacks.
#   * Reserve is a straight deduction from the settlement (no return of the reserve is modelled).
#   * No rounding inside the computation; framework rounds each result half-up to 2 dp (USD).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h088"


def solve(text: str, q: dict) -> dict:
    G = grab(r"gross sales before chargebacks of {N}", text)
    n = grab(r"across {N} transactions", text)
    r = grab(r"charges rate {N} on those gross sales", text)
    c = grab(r"gross sales plus {N} per transaction", text)
    cb = grab(r"Chargebacks included in the gross-sales amount total {N}", text)
    f = grab(r"of which fraction {N} is recovered", text)
    reserve = grab(r"withholds reserve {N}", text)

    variable_fee = r * G
    fixed_fee = c * n
    unrecovered = cb * (1 - f)
    net = G - variable_fee - fixed_fee - unrecovered - reserve

    return {
        "final": net,
        "slots": {
            "variable_fee_checkpoint": variable_fee,
            "fixed_fee_checkpoint": fixed_fee,
            "chargeback_loss_checkpoint": unrecovered,
        },
    }
