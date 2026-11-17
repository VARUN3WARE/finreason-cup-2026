from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.supply_chain_npv_net_benefit.advanced.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"[Ss]upply-chain spend is {N} and {N}", text)
    red = grab(r"annual cost reduction is {N} percent", text) / 100
    horizon = grab(r"savings horizon is {N} years?", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    integ = grab(r"integration cost is {N}", text)
    if horizon.denominator != 1:
        raise ValueError(f"non-integer horizon {horizon}")
    n = int(horizon)
    saving = (a + b) * red
    npv = sum((saving / (1 + r) ** t for t in range(1, n + 1)), Fraction(0))
    net = npv - integ
    return {"final": net, "slots": {"trace_1": saving, "trace_2": npv}}
