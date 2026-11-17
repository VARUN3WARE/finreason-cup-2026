from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.deal_structure.control_premium_debt_earnout_calculation.advanced.v1"


def solve(text: str, q: dict) -> dict:
    base = grab(r"[Bb]ase purchase price is {N} USD", text)
    prem_pct = grab(r"control premium is {N} percent of base price", text)
    max_eo = grab(r"maximum earn-out is {N} USD", text)
    ach_pct = grab(r"performance achievement is {N} percent", text)
    debt_pct = grab(r"debt financing is {N} percent of total consideration", text)

    premium = base * prem_pct / 100
    prorated = max_eo * ach_pct / 100
    total = base + premium + prorated
    equity = total * (1 - debt_pct / 100)
    return {"final": equity, "slots": {"trace_1": premium, "trace_2": total}}
