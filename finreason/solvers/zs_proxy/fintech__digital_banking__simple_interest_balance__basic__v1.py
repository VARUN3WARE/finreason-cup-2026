from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.digital_banking.simple_interest_balance.basic.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"starts with {N} USD", text)
    r = grab(r"simple annual interest of {N} percent", text) / 100
    t = grab(r"remains open for {N} years?", text)
    interest = p * r * t
    return {"final": p + interest, "slots": {"simple_interest_trace": interest}}
