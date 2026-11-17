# FINANCE MODEL (h073): break-even / target-return maximum purchase price, per share, USD.
#
#   G  = gross terminal sale proceeds
#   D  = holding-period dividend cash (received, not reinvested, not discounted)
#   X  = exit cost (deducted from the sale)
#   E  = entry cost (added on top of the quoted purchase price)
#   t  = target total return, as a plain ratio (0.25 = 25%; 2 = 200%)
#
#   Net terminal receipts   R = G + D - X                      (checkpoint 1; unrounded, framework rounds to cents)
#   Complete acquisition outlay  C = P + E                     (P = quoted purchase price)
#   Simple, non-annualised total return = (R - C) / C
#   Set (R - C)/C = t   =>   C = R / (1 + t)   =>   P* = R / (1 + t) - E
#
#   Final answer = exact threshold P* (unrounded; framework applies half-up to cents).
#   No taxes, financing, discounting, or reinvestment. The threshold is NOT floored to a whole-cent
#   quote (the text says the displayed value is a rounded report of the exact threshold).
#   Overrides of standard conventions: none. Dividends are part of the receipts R (otherwise the
#   dividend input would be unused and the checkpoint wording "terminal receipts" covers all cash in).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h073"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross terminal sale proceeds {N}", text)
    div = grab(r"holding-period dividend cash {N}", text)
    exit_cost = grab(r"exit cost {N}", text)
    entry_cost = grab(r"entry cost {N}", text)
    target = grab(r"target ratio {N}", text)

    net_receipts = gross + div - exit_cost
    outlay = net_receipts / (1 + target)
    price = outlay - entry_cost
    return {"final": price, "slots": {"net_receipts_checkpoint": net_receipts}}
