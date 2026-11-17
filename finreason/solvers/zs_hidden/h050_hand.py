"""h050: two-plan transfer-fee comparison (rate on volume + per-transfer fee + monthly
subscription + one-time setup fee); final = Plan B total minus Plan A total (signed)."""
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h050"



def solve(text: str, q: dict) -> dict:
    vol = grab(r"monthly transfer volume\s+{N}", text)
    cnt = grab(r"\s{N}\s+transfers per month", text)
    months = grab(r"transfers per month for\s+{N}\s+months?", text)

    a_rate, a_fee, a_sub, a_setup = grab_all(
        r"Plan A charges proportional transfer rate\s+{N},\s*fee\s+{N}\s+per transfer,"
        r"\s*monthly subscription\s+{N},\s*and one-time setup fee\s+{N}",
        text,
    )
    b_rate, b_fee, b_sub, b_setup = grab_all(
        r"Plan B charges\s+{N},\s*{N},\s*{N},\s*and one-time setup fee\s+{N}",
        text,
    )

    total_volume = vol * months
    total_count = cnt * months

    def cost(rate, fee, sub, setup):
        # setup fee charged exactly once; subscription monthly; fee per transfer
        return rate * total_volume + fee * total_count + sub * months + setup

    cost_a = cost(a_rate, a_fee, a_sub, a_setup)
    cost_b = cost(b_rate, b_fee, b_sub, b_setup)
    savings = cost_b - cost_a

    return {
        "final": Fraction(savings),
        "slots": {
            "horizon_volume_checkpoint": Fraction(total_volume),
            "horizon_count_checkpoint": Fraction(total_count),
        },
    }
