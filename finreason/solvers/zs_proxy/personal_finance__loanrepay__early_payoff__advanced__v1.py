import re
from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.loanrepay.early_payoff.advanced.v1"


def solve(text: str, q: dict) -> dict:
    balance = grab(r"Outstanding balance in USD is {N}", text)
    interest = grab(r"Accrued interest in USD is {N}", text)
    ratio = grab(r"Penalty ratio is {N}", text)
    if re.search(r"Penalty ratio is \S+ percent", text):
        ratio = ratio / 100
    cash = grab(r"Available cash in USD is {N}", text)
    m = re.search(r"Penalty-waived flag is (true|false|True|False|yes|no)\b", text)
    if m is None:
        raise ValueError("waived flag not found")
    waived = m.group(1).lower() in ("true", "yes")

    scheduled_penalty = balance * ratio
    effective_penalty = Fraction(0) if waived else scheduled_penalty
    payoff_due = balance + interest + effective_penalty
    surplus = cash - payoff_due
    affordable = surplus >= 0  # true at zero or positive surplus
    return {
        "final": "true" if affordable else "false",
        "slots": {
            "effective_penalty_usd": effective_penalty,
            "payoff_due_usd": payoff_due,
            "cash_surplus_usd": surplus,
        },
    }
