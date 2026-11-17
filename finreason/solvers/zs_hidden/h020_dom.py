# FINANCE MODEL (fictional enforcement remedy with cooperation credit)
#
#   M  = maximum total remedy (USD)            -- hard ceiling on penalty + interest
#   I  = fixed interest (USD), part of M       -- not reducible by cooperation credit
#   cap = M - I                                -- amount of the ceiling available for the penalty
#   G  = realized gain (USD), k = multiplier   -- gain-based penalty = G * k
#   S  = alternative statutory floor (USD)
#   B  = pre-credit penalty base = max(G * k, S)   ("greater of those two amounts")
#   c  = cooperation credit ratio; credited penalty = (1 - c) * B
#
#   Solve for c such that credited penalty + fixed interest == M:
#       (1 - c) * B + I = M   =>   (1 - c) = (M - I) / B = cap / B
#       c = 1 - cap / B                       (ratio)
#       credit percentage = 100 * c           (unit: percent)
#
# Conventions / overrides:
#   - Fictional scenario: only rules stated in the text are applied (no real-world law).
#   - Checkpoint "penalty_cap_checkpoint" = cap = M - I in USD (unrounded exact value is returned;
#     the framework applies half-up to 2 dp).  Final answer is computed from the exact (unrounded) cap
#     and exact B -- no intermediate rounding ("independent" rounding of each reported value).
#   - No clamping of c: the text asks which c makes the equation hold; the value is returned as is
#     (all three instances have 0 < c < 1 anyway, i.e. cap < B so a credit is genuinely needed).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h020"


def solve(text: str, q: dict) -> dict:
    M = grab(r"maximum total remedy is {N} USD", text)
    I = grab(r"of which {N} USD is fixed interest", text)
    G = grab(r"realized gain {N} USD multiplied by", text)
    k = grab(r"realized gain {N} USD multiplied by {N}", text, group=2)
    S = grab(r"statutory floor is {N} USD", text)

    cap = M - I
    gain_penalty = G * k
    base = gain_penalty if gain_penalty >= S else S  # greater of the two
    c = 1 - cap / base
    return {"final": c * 100, "slots": {"penalty_cap_checkpoint": cap}}
