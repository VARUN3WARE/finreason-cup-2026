from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.current_ratio_with_adjustment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"Current assets are {N} USD", text)
    cl = grab(r"current liabilities before reclassification are {N} USD", text)
    reclass = grab(r"long-term loan, {N} USD becomes current", text)
    r0 = ca / cl
    cl_adj = cl + reclass
    r1 = ca / cl_adj
    return {
        "final": r0 - r1,
        "slots": {"trace_1": r0, "trace_2": cl_adj, "trace_3": r1},
    }
