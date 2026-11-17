# FINANCE MODEL (h070): reverse-solving a gross transfer through a staged fee/rebate chain.
#
# Forward chain on a gross transfer G (USD):
#   stage 1: proportional fee at ratio f   -> amount after stage 1 = G * (1 - f)   (retention ratio = 1 - f)
#   stage 2: fixed network fee c           -> amount after stage 2 = G * (1 - f) - c
#   stage 3: rebate b credited (added)     -> recipient obtains  R = G * (1 - f) - c + b
#
# Reverse (as the text prescribes, in order):
#   step 1: remove the rebate        -> receipt required BEFORE applying the rebate: P = R - b
#           (this is the amount the recipient must hold after the proportional and fixed fees,
#            i.e. G * (1 - f) - c; it is checkpoint "pre_rebate_checkpoint", position 1)
#   step 2: restore the fixed fee    -> P + c   (= G * (1 - f))
#   step 3: divide by retention (1-f)-> G = (P + c) / (1 - f)
#
# Conventions / overrides: "proportional fee ratio of 0.2" is a plain ratio (20 %), NOT a percent
# number to divide again; retention = 1 - ratio. Everything exact (Fraction); final answer rounded
# half-up to 2 dp by the framework, nothing rounded inside the computation.
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h070"


def solve(text: str, q: dict) -> dict:
    f = grab(r"proportional fee ratio of {N}", text)
    fee = grab(r"fixed network fee of {N} USD", text)
    rebate = grab(r"rebate of {N} USD", text)
    target = grab(r"recipient to obtain exactly {N} USD", text)

    retention = 1 - f
    pre_rebate = target - rebate          # receipt required before the rebate is applied
    pre_fixed = pre_rebate + fee          # after restoring the fixed fee
    gross = pre_fixed / retention         # after dividing by the retention ratio

    return {"final": gross, "slots": {"pre_rebate_checkpoint": pre_rebate}}
