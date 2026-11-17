"""h015 -- distributable earnings x payout-ratchet factor, capped by a liquidity limit.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction
import re

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h015"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stage_count(text: str) -> int:
    m = re.search(r"exactly (\w+) sequential payout-ratchet stages?", text)
    if m is None:
        m = re.search(r"(\w+) sequential payout-ratchet stages?", text)
    tok = m.group(1).lower()
    if tok.isdigit():
        return int(tok)
    return _WORDS[tok]


def solve(text: str, q: dict) -> dict:
    # S1: "A company forecasts net income of X and must first retain R, ... USD millions."
    net_income = grab(r"forecasts net income of {N}", text)
    retention = grab(r"must first retain {N}", text)
    # Distributable earnings = net income less the amount that must first be retained.
    distributable = net_income - retention

    # S2: "dividend authorization starts at 100% of distributable earnings and passes
    #      through exactly n sequential payout-ratchet stages."
    start_share = grab(r"authorization starts at {N}\s*%", text) / 100
    n_stages = _stage_count(text)

    # S3: "Each stage reduces the remaining authorized share by the same fraction t,
    #      so the policy limit is distributable earnings times (1-t)^n."
    t = grab(r"same fraction t\s*=\s*{N}", text)
    # Authorized share remaining after one ratchet stage (checkpoint).
    one_stage_factor = start_share * (1 - t)
    share = start_share
    for _ in range(n_stages):
        share = share * (1 - t)
    policy_limit = distributable * share

    # S4: "The liquidity plan separately caps the cash dividend at C."
    liquidity_cap = grab(r"caps the cash dividend at {N}", text)

    # S5: maximum total cash dividend satisfying both limits.
    dividend = min(policy_limit, liquidity_cap)
    if dividend < 0:
        dividend = Fraction(0)

    return {
        "final": dividend,
        "slots": {"one_stage_payout_factor_checkpoint": one_stage_factor},
    }
