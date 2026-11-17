import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.basel.leverage_ratio.basic.v1"


def _meets(value: Fraction, text: str) -> bool:
    m = re.search(r"(inclusive|exclusive|strict)\s+(" + NUMBER + r") percent threshold", text)
    if m is None:
        # fall back: "at least X percent" (inclusive) / "above X percent" (strict)
        thr = grab(r"(?:at least|above|exceed(?:s|ing)?|more than|greater than) {N} percent", text)
        strict = re.search(r"(?:above|exceed(?:s|ing)?|more than|greater than) " + NUMBER + r" percent", text) is not None
    else:
        thr = F(m.group(2))
        strict = m.group(1) != "inclusive"
    return value > thr if strict else value >= thr


def solve(text: str, q: dict) -> dict:
    t1 = grab(r"Tier 1 capital in USD millions is {N}", text)
    exposure = grab(r"Exposure in USD millions is {N}", text)
    lev_pct = t1 / exposure * 100
    ok = _meets(lev_pct, text)
    return {"final": "true" if ok else "false", "slots": {"leverage_percent": lev_pct}}
