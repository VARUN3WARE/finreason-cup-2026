"""h051: two-state call vs put comparison with qualification thresholds."""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h051"


def _prob(text: str, word: str) -> Fraction:
    p = grab(word + r" probability (?:of )?{N}(\s*(?:%|percent))?", text)
    m = re.search(word + r" probability (?:of )?[-\d.,/]+\s*(%|percent)", text)
    if m:
        p = p / 100
    return p


def solve(text: str, q: dict) -> dict:
    s_bull = grab(r"bullish terminal price {N}", text)
    s_bear = grab(r"bearish terminal price {N}", text)
    try:
        p_bull = _prob(text, "bullish")
    except ValueError:
        p_bull = 1 - _prob(text, "bearish")
    p_bear = 1 - p_bull

    k_call = grab(r"call with strike {N}", text)
    k_put = grab(r"put with strike {N}", text)
    c_prem = grab(r"call premium {N}", text)
    p_prem = grab(r"put premium {N}", text)

    min_ep = grab(r"expected profit is at least {N}", text)
    min_worst = grab(r"worst-state profit is at least {N}", text)

    # Payoffs per state (general max(0, .) form; strikes lie strictly between prices).
    call_bull = max(Fraction(0), s_bull - k_call)
    call_bear = max(Fraction(0), s_bear - k_call)
    put_bull = max(Fraction(0), k_put - s_bull)
    put_bear = max(Fraction(0), k_put - s_bear)

    call_ep = p_bull * call_bull + p_bear * call_bear - c_prem
    put_ep = p_bull * put_bull + p_bear * put_bear - p_prem
    call_worst = min(call_bull, call_bear) - c_prem
    put_worst = min(put_bull, put_bear) - p_prem

    call_q = call_ep >= min_ep and call_worst >= min_worst
    put_q = put_ep >= min_ep and put_worst >= min_worst

    if call_q and put_q:
        final = "Call" if call_ep >= put_ep else "Put"
    elif call_q:
        final = "Call"
    elif put_q:
        final = "Put"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "call_payoff_checkpoint": call_bull,
            "put_payoff_checkpoint": put_bear,
        },
    }
