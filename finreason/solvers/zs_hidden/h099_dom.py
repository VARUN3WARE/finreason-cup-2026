# FINANCE MODEL (h099): sequential shock then rebound, solve backwards for the pre-shock price.
#
#   P0 = pre-shock price (unknown)
#   L  = shock loss ratio (given, e.g. 0.2 means a 20% drop)
#   m  = relative-magnitude multiplier (given: "m times the shock loss ratio")
#   R  = rebound ratio = m * L          (checkpoint 1, plain ratio, NOT percent)
#   P1 = post-shock price = P0 * (1 - L)
#   P2 = post-rebound price = P1 * (1 + R)   -> this is the CURRENT price quoted in the text
#
#   Therefore P0 = P2 / ((1 - L) * (1 + R)).
#
# Conventions / notes:
#   - Loss and rebound are applied sequentially and multiplicatively (rebound is on the post-shock
#     price, NOT on the pre-shock price), so the path is not symmetric (P2 != P0 unless R = L/(1-L)).
#   - "currently priced at X" is the price AFTER both the shock and the rebound.
#   - The multiplier may be written as a decimal or a rational such as 4/3; the NUMBER regex
#     in finreason.nums parses rationals exactly.
#   - Final answer is returned unrounded; framework rounds half-up to 2 dp (usd).
#   - Checkpoint rebound ratio R = m * L unrounded; framework rounds to 6 dp (ratio).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h099"


def solve(text: str, q: dict) -> dict:
    p2 = grab(r"currently priced at {N} USD", text)
    loss = grab(r"loss ratio {N}", text)
    mult = grab(r"rebound ratio equal to {N} times the shock loss ratio", text)

    rebound = mult * loss
    p1 = p2 / (1 + rebound)      # post-shock price (before rebound)
    p0 = p1 / (1 - loss)         # pre-shock price

    return {"final": p0, "slots": {"rebound_ratio_checkpoint": rebound}}
