from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.digital_banking.transfer_total_deduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    amount = grab(r"sends {N} USD", text)
    rate = grab(r"charges {N} percent of the transfer amount", text) / 100
    fee = amount * rate
    return {"final": amount + fee, "slots": {"fee_amount_trace": fee}}
