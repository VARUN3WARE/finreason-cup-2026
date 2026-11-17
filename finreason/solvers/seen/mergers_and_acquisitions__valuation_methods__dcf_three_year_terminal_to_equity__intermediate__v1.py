from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.valuation_methods.dcf_three_year_terminal_to_equity.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    fcfs = grab_all(r"Years 1 through 3 are {N},? {N},? and {N} USD million", text)
    r = grab(r"discount rate is {N} percent", text) / 100
    g = grab(r"terminal growth rate is {N} percent", text) / 100
    debt = grab(r"total debt is {N} USD million", text)
    cash = grab(r"\bcash is {N} USD million", text)
    pv_fcf = sum((cf / (1 + r) ** t for t, cf in enumerate(fcfs, start=1)), Fraction(0))
    tv = fcfs[2] * (1 + g) / (r - g)
    pv_tv = tv / (1 + r) ** 3
    equity = pv_fcf + pv_tv - debt + cash
    # trace_1 = sum of forecast PVs, trace_2 = PV of terminal value
    return {"final": equity, "slots": {"trace_1": pv_fcf, "trace_2": pv_tv}}
