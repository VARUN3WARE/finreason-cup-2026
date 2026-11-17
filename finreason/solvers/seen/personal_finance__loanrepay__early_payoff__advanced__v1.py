import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.loanrepay.early_payoff.advanced.v1"

_TRUE = {"true", "yes"}
_FALSE = {"false", "no"}


def _flag(text: str) -> bool:
    m = re.search(r"[Pp]enalty-waived flag is\s+([A-Za-z]+)", text)
    if m is None:
        raise ValueError("penalty-waived flag not found")
    tok = m.group(1).lower()
    if tok in _TRUE:
        return True
    if tok in _FALSE:
        return False
    raise ValueError(f"unrecognised waived flag {tok!r}")


def solve(text: str, q: dict) -> dict:
    balance = grab(r"Outstanding balance in USD is {N}", text)
    interest = grab(r"Accrued interest in USD is {N}", text)
    ratio = grab(r"Penalty ratio is {N}", text)  # plain ratio (not percent)
    cash = grab(r"Available cash in USD is {N}", text)
    waived = _flag(text)

    scheduled_penalty = balance * ratio
    effective_penalty = Fraction(0) if waived else scheduled_penalty
    payoff_due = balance + interest + effective_penalty
    surplus = cash - payoff_due
    affordable = "true" if surplus >= 0 else "false"  # zero surplus counts as affordable
    return {
        "final": affordable,
        "slots": {
            "effective_penalty_usd": effective_penalty,
            "payoff_due_usd": payoff_due,
            "cash_surplus_usd": surplus,
        },
    }
