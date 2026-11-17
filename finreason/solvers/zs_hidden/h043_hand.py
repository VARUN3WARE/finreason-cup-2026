"""h043: inverse WACC -- maximum pre-tax cost of debt that keeps WACC at a ceiling.

WACC = E/V * re + D/V * rd * (1 - t),  V = E + D
Written with the debt-to-equity ratio d = D/E:
    WACC = re / (1 + d) + rd * (1 - t) * d / (1 + d)
=>  rd   = (WACC * (1 + d) - re) / (d * (1 - t))
WACC is increasing in rd, so the rd giving WACC == ceiling is the maximum allowed.
"""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h043"


def _rate(text: str, label: str) -> Fraction:
    """Read a rate given either as 'label percentage X' / 'label percent X' or 'label ratio X'.

    Returns the value as a ratio (decimal).
    """
    m = re.search(label + r"\s+(percentage|percent|ratio|rate)\s+(?:of\s+|is\s+)?", text, flags=re.I)
    if m is None:
        raise ValueError(f"rate label not found: {label}")
    kind = m.group(1).lower()
    v = grab(re.escape(m.group(0)) + r"{N}", text)
    if kind in ("percentage", "percent"):
        return v / 100
    return v


def solve(text: str, q: dict) -> dict:
    E = grab(r"equity value (?:of |is )?{N}", text)
    D = grab(r"debt value (?:of |is )?{N}", text)
    re_ = _rate(text, r"cost of equity")
    t = _rate(text, r"(?:corporate )?tax rate")

    # WACC ceiling: stated as a percentage ("The WACC ceiling X is also a percentage").
    w = grab(r"WACC ceiling (?:of |is )?{N}", text)
    # Sentence containing the ceiling (split on ". " so decimals like 10.1875 are not cut).
    sent = re.split(r"\.\s", text[text.find("WACC ceiling"):], maxsplit=1)[0]
    is_ratio = re.search(r"\bratio\b", sent) and not re.search(r"percent", sent)
    if not is_ratio:
        w = w / 100

    d = D / E  # debt-to-equity ratio
    rd = (w * (1 + d) - re_) / (d * (1 - t))

    return {
        "final": rd * 100,  # percent
        "slots": {"debt_to_equity_checkpoint": d},
    }
