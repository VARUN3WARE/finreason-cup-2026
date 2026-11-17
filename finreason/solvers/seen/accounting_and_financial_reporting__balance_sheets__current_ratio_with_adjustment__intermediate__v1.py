from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.balance_sheets.current_ratio_with_adjustment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"Current assets are {N} USD", text)
    cl = grab(r"current liabilities before reclassification are {N} USD", text)
    reclass = grab(r"long-term loan, {N} USD becomes current", text)

    initial = ca / cl
    adj_cl = cl + reclass
    adjusted = ca / adj_cl
    # Decrease = initial - adjusted (sign preserved; unrounded ratios used).
    return {"final": initial - adjusted, "slots": {"trace_1": initial, "trace_2": adj_cl, "trace_3": adjusted}}
