from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h088"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross sales before chargebacks of\s+\$?{N}", text)
    n_tx = grab(r"across\s+{N}\s+transactions", text)
    rate = grab(r"charges rate\s+{N}", text)
    per_tx = grab(r"plus\s+\$?{N}\s+per transaction", text)
    cb = grab(r"total\s+\$?{N},\s+of which", text)
    rec = grab(r"of which fraction\s+{N}\s+is recovered", text)
    reserve = grab(r"withholds reserve\s+\$?{N}", text)

    variable_fee = rate * gross                 # proportional fee on gross sales (chargebacks included)
    fixed_fee = per_tx * n_tx                   # aggregate per-transaction fees
    unrecovered = cb * (1 - rec)                # chargeback loss not recovered
    net = gross - variable_fee - fixed_fee - unrecovered - reserve

    return {
        "final": net,
        "slots": {
            "variable_fee_checkpoint": variable_fee,
            "fixed_fee_checkpoint": fixed_fee,
            "chargeback_loss_checkpoint": unrecovered,
        },
    }
