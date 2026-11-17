"""h073: binding quoted purchase price for a target simple total return.

net receipts R = gross terminal proceeds + holding-period dividends - exit cost
outlay O = quote P + entry cost
total return = (R - O) / O = target  ->  O = R / (1 + target),  P = O - entry
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h073"


def _target(text: str) -> Fraction:
    try:
        return grab(r"target ratio\s+{N}", text)
    except ValueError:
        pass
    try:
        return grab(r"target (?:total )?return (?:of )?{N}\s*(?:percent|%)", text) / 100
    except ValueError:
        return grab(r"target[^0-9\-]*{N}", text)


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross terminal sale proceeds\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    div = grab(r"dividend cash\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    exit_cost = grab(r"exit cost\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    entry_cost = grab(r"entry cost\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    target = _target(text)

    net_receipts = gross + div - exit_cost
    outlay = net_receipts / (1 + target)
    quote = outlay - entry_cost

    return {"final": quote, "slots": {"net_receipts_checkpoint": net_receipts}}
