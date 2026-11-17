from fractions import Fraction
import re

from finreason.nums import grab

TEMPLATE_ID = "h082"


def _avail(text: str) -> bool:
    m = re.search(r"operational availability\s+(true|false|yes|no)", text, flags=re.I)
    if m is None:
        raise ValueError("availability not found")
    return m.group(1).lower() in ("true", "yes")


def solve(text: str, q: dict) -> dict:
    obligation = grab(r"compliance obligation of {N}", text)
    capacity = grab(r"abatement capacity {N}", text)
    available = _avail(text)
    fixed = grab(r"fixed cost {N}", text)
    var_rate = grab(r"variable cost {N}", text)
    credit_price = grab(r"[Cc]redits cost {N}", text)
    credit_cap = grab(r"at most {N} ton-equivalent credits", text)

    # Abate-then-buy: fixed rule, abate min(obligation, capacity), buy residual credits.
    if available:
        abate_qty = min(obligation, capacity)
        variable_total = abate_qty * var_rate
        residual = obligation - abate_qty
        atb_feasible = residual <= credit_cap
        atb_cost = fixed + variable_total + residual * credit_price
    else:
        abate_qty = Fraction(0)
        variable_total = Fraction(0)
        atb_feasible = False
        atb_cost = None

    # Credits-only: buy credits for the whole obligation.
    co_feasible = obligation <= credit_cap
    co_cost = obligation * credit_price

    if atb_feasible and co_feasible:
        final = "abate_then_buy" if atb_cost <= co_cost else "credits_only"
    elif atb_feasible:
        final = "abate_then_buy"
    elif co_feasible:
        final = "credits_only"
    else:
        final = "no_feasible_strategy"

    return {"final": final, "slots": {"variable_abatement_total_checkpoint": variable_total}}
