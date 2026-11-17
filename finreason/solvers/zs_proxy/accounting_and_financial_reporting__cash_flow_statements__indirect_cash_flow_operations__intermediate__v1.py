import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.cash_flow_statements.indirect_cash_flow_operations.intermediate.v1"


def _change(label: str, text: str) -> Fraction:
    """Signed change of a balance: increase -> +amount, decrease -> -amount."""
    m = re.search(label + r"\s+(increase|decrease)s?\s+by\s+(?:USD\s+)?(" + NUMBER + ")", text, flags=re.I)
    if m is None:
        raise ValueError(f"no change found for {label!r}")
    amt = F(m.group(2))
    return amt if m.group(1).lower() == "increase" else -amt


def solve(text: str, q: dict) -> dict:
    ni = grab(r"Net income is\s+(?:USD\s+)?{N}", text)
    dep = grab(r"Depreciation is\s+(?:USD\s+)?{N}", text)
    amort = grab(r"amortization is\s+(?:USD\s+)?{N}", text)
    d_ar = _change(r"[Aa]ccounts receivable", text)
    d_inv = _change(r"[Ii]nventory", text)
    d_ap = _change(r"[Aa]ccounts payable", text)
    d_accr = _change(r"[Aa]ccrued expenses", text)
    da = dep + amort
    # Operating current assets: increase uses cash; operating current liabilities: increase provides cash.
    wc_adj = -d_ar - d_inv + d_ap + d_accr
    return {"final": ni + da + wc_adj, "slots": {"trace_1": da, "trace_2": wc_adj}}
