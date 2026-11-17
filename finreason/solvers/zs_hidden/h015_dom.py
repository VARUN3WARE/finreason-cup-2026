# FINANCE MODEL
# -------------
# Net income NI is forecast. A fixed amount R must first be retained (set aside), so
#   distributable earnings  D = max(0, NI - R)            (cannot distribute a negative amount)
# Fictional ratchet policy: authorization starts at 100% of D and passes through n sequential
# stages; each stage multiplies the remaining authorized share by (1 - t).
#   one-stage payout factor  f = 1 - t                    (checkpoint, plain ratio)
#   policy limit             L = D * f**n                 (integer power, exact)
# Separate liquidity cap C on the cash dividend (USD million).
# Maximum total cash dividend satisfying both limits = min(L, C)  (non-negative).
# No overrides of standard conventions; no rounding inside the chain (framework rounds
# the final value half up to 2 dp in USD million, checkpoint to 6 dp as ratio).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h015"

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
          "eight": 8, "nine": 9, "ten": 10}


def solve(text: str, q: dict) -> dict:
    ni = grab(r"forecasts net income of {N}", text)
    retain = grab(r"must first retain {N}", text)
    t = grab(r"fraction t\s*=\s*{N}", text)
    cap = grab(r"caps the cash dividend at {N}", text)
    import re
    m = re.search(r"exactly (\w+) sequential", text)
    w = m.group(1).lower()
    n = _WORDS[w] if w in _WORDS else int(w)

    dist = max(Fraction(0), ni - retain)
    f = 1 - t
    policy_limit = dist * f ** n
    final = min(policy_limit, cap)
    if final < 0:
        final = Fraction(0)
    return {"final": final, "slots": {"one_stage_payout_factor_checkpoint": f}}
