import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.basel.rwa_increase.intermediate.v1"


def _meets(value: Fraction, text: str) -> bool:
    m = re.search(r"(inclusive|exclusive|strict)\s+(" + NUMBER + r") percent threshold", text)
    if m is None:
        thr = grab(r"(?:at least|above|exceed(?:s|ing)?|more than|greater than) {N} percent", text)
        strict = re.search(r"(?:above|exceed(?:s|ing)?|more than|greater than) " + NUMBER + r" percent", text) is not None
    else:
        thr = F(m.group(2))
        strict = m.group(1) != "inclusive"
    return value > thr if strict else value >= thr


def solve(text: str, q: dict) -> dict:
    cap = grab(r"[Tt]otal capital in USD millions is {N}", text)
    cur = grab(r"[Cc]urrent risk-weighted assets in USD millions (?:are|is) {N}", text)
    inc = grab(r"RWA increase in USD millions is {N}", text)
    new_rwa = cur + inc
    cap_pct = cap / new_rwa * 100
    ok = _meets(cap_pct, text)
    return {
        "final": "true" if ok else "false",
        "slots": {"new_rwa_usd_million": new_rwa, "new_capital_percent": cap_pct},
    }
