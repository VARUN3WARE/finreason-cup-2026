import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.indirect_cash_flow_operations.intermediate.v1"


def _signed_change(label: str, text: str) -> Fraction:
    """Balance change for an item, +amount for an increase, -amount for a decrease."""
    m = re.search(
        label + r"\s+(increases?|decreases?|rises?|falls?|declines?)\s+by\s+(" + NUMBER + ")",
        text,
        flags=re.I | re.S,
    )
    if m is None:
        raise ValueError(f"working-capital item not found: {label}")
    amount = Fraction(m.group(2).replace(",", ""))
    word = m.group(1).lower()
    if word.startswith(("decrease", "fall", "decline")):
        amount = -amount
    return amount


def solve(text: str, q: dict) -> dict:
    ni = grab(r"[Nn]et income is {N}", text)
    dep = grab(r"[Dd]epreciation is {N}", text)
    amort = grab(r"amortization is {N}", text)
    d_ar = _signed_change(r"[Aa]ccounts receivable", text)
    d_inv = _signed_change(r"[Ii]nventory", text)
    d_ap = _signed_change(r"[Aa]ccounts payable", text)
    d_accr = _signed_change(r"[Aa]ccrued expenses", text)
    da = dep + amort
    # Increase in operating assets uses cash; increase in operating liabilities provides cash.
    wc_adj = -d_ar - d_inv + d_ap + d_accr
    return {"final": Fraction(ni + da + wc_adj), "slots": {"trace_1": da, "trace_2": wc_adj}}
