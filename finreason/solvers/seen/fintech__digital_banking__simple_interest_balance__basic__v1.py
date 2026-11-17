from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.digital_banking.simple_interest_balance.basic.v1"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"starts with {N} USD", text)
    rate = grab(r"simple annual interest of {N} percent", text) / 100
    years = grab(r"remains open for {N} years?", text)
    interest = principal * rate * years
    return {"final": principal + interest, "slots": {"simple_interest_trace": interest}}
