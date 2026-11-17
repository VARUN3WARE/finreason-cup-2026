"""h033 -- three-stage stressed token price, burn vs emission policy with a market-cap floor test.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h033"


def solve(text: str, q: dict) -> dict:
    # S1: "A token has {N} units and a current price of {N} USD."
    units = grab(r"A token has {N} units", text)
    current_price = grab(r"current price of {N} USD", text)

    # S2: "In each of exactly three sequential stress stages, the same ratio {d} is removed from the
    #      price surviving the previous stage, with no replenishment between stages; the three-stage
    #      stressed price is therefore current price times (1-per-stage downside ratio)^3."
    n_stages = 3
    downside_ratio = grab(r"the same ratio {N} is removed from the price", text)
    retention_one_stage = 1 - downside_ratio  # price-retention ratio after one stress stage
    stressed_price = current_price * retention_one_stage ** n_stages

    # S3: "Under the burn policy, {b} units are removed and treasury support raises that stressed
    #      price once by ratio {s}."
    burn_units_removed = grab(r"burn policy, {N} units are removed", text)
    support_ratio = grab(r"raises that stressed price once by ratio {N}", text)
    burn_units = units - burn_units_removed
    burn_price = stressed_price * (1 + support_ratio)
    burn_cap = burn_units * burn_price

    # S4: "Under the fallback emission policy, {e} units are added and the stressed price receives
    #      no support."
    emission_units_added = grab(r"emission policy, {N} units are added", text)
    emission_units = units + emission_units_added
    emission_price = stressed_price
    emission_cap = emission_units * emission_price

    # S5: "Ignore any other price effects." -- nothing else applied.

    # S6: "Use the burn policy if its resulting market cap is at least {F} USD; otherwise use the
    #      emission policy."
    floor = grab(r"market cap is at least {N} USD", text)
    if burn_cap >= floor:
        selected_cap = burn_cap
    else:
        selected_cap = emission_cap

    # S7: "What market cap is selected?" -- exact, framework rounds half-up to 2 dp.
    return {
        "final": selected_cap,
        "slots": {"one_stage_price_retention_checkpoint": retention_one_stage},
    }
