from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.digital_banking.highest_spend_amount.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"Category A is {N} USD", text)
    b = grab(r"Category B is {N} USD", text)
    c = grab(r"Category C is {N} USD", text)
    ab = max(a, b)
    return {"final": max(ab, c), "slots": {"max_a_b_trace": ab}}
