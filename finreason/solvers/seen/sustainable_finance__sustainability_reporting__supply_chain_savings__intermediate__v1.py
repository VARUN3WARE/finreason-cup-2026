from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.supply_chain_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"Annual supply-chain cost is {N} USD", text)
    fixed = grab(r"fixed saving of {N} USD", text)
    pct = grab(r"additional {N} percent saving", text)
    remaining = cost - fixed
    additional = remaining * pct / 100
    return {
        "final": fixed + additional,
        "slots": {"remaining_cost_trace": remaining, "additional_saving_trace": additional},
    }
