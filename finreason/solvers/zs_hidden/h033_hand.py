from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h033"


def solve(text: str, q: dict) -> dict:
    units = grab(r"token has {N} units", text)
    price = grab(r"current price of {N} USD", text)
    d = grab(r"the same ratio {N} is removed", text)
    stages = 3  # "exactly three sequential stress stages" / "(1-per-stage downside ratio)^3"
    burn_units = grab(r"burn policy, {N} units are removed", text)
    support = grab(r"raises that stressed price once by ratio {N}", text)
    emit_units = grab(r"emission policy, {N} units are added", text)
    floor = grab(r"resulting market cap is at least {N} USD", text)

    retention = 1 - d
    stressed = price * retention ** stages
    burn_cap = (units - burn_units) * stressed * (1 + support)
    emit_cap = (units + emit_units) * stressed
    final = burn_cap if burn_cap >= floor else emit_cap
    return {"final": final, "slots": {"one_stage_price_retention_checkpoint": retention}}
