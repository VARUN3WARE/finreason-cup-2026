"""h054: two-state inventory sale -> quick-ratio convexity premium (Jensen gap).

Structure (from the text):
  * pre-sale quick assets (excluding inventory) Q0; inventory carrying amount I is sold;
  * net proceeds in a state = recovery rate x carrying amount;
  * fraction k of proceeds stays as cash in quick assets, (1 - k) repays current liabilities at par;
  * low rate r_L, high rate r_H = r_L + spread; high state probability p;
  * liabilities remaining after HIGH-state repayment are given -> implied pre-sale liabilities
    L0 = given + (1 - k) * r_H * I, identical in both states.
  * per-state quick ratio QR_s = (Q0 + k*N_s) / (L0 - (1-k)*N_s)
  * premium = [p*QR_H + (1-p)*QR_L] - [E(QA) / E(L)], reported in percentage points (x100).
Checkpoints:
  1. retained cash in low state = k * r_L * I
  2. high-state increment in retained cash = k * (r_H - r_L) * I
  3. high-state increment in liability repayment = (1 - k) * (r_H - r_L) * I
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h054"


def _rate(pattern: str, text: str) -> Fraction:
    """Parse a rate; accept either a plain ratio or a value followed by 'percent'."""
    import re
    from finreason.nums import NUMBER

    rx = pattern.replace("{N}", f"({NUMBER})") + r"(\s*(?:percent|%))?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    q0 = grab(r"Quick assets before the sale, excluding inventory, are {N}", text)
    inv = grab(r"inventory carrying amount {N}", text)
    keep = _rate(r"fraction {N}", text)
    r_low = _rate(r"low recovery rate is {N}", text)
    spread = _rate(r"positive spread {N}", text)
    r_high = r_low + spread
    p_high = _rate(r"high state occurs with probability {N}", text)
    p_low = 1 - p_high

    proceeds_low = r_low * inv
    proceeds_high = r_high * inv
    cash_low = keep * proceeds_low
    cash_high = keep * proceeds_high
    repay_low = (1 - keep) * proceeds_low
    repay_high = (1 - keep) * proceeds_high

    # Implied pre-sale liabilities from the given post-repayment figure.
    import re
    from finreason.nums import NUMBER

    m = re.search(
        rf"gives ({NUMBER}) USD, the liabilities remaining after (high|low)-state repayment",
        text,
    )
    if m is None:
        given = grab(r"gives {N} USD, the liabilities remaining after", text)
        state = "high"
    else:
        given = Fraction(m.group(1).replace(",", ""))
        state = m.group(2)
    l0 = given + (repay_high if state == "high" else repay_low)

    qa_low = q0 + cash_low
    qa_high = q0 + cash_high
    li_low = l0 - repay_low
    li_high = l0 - repay_high

    qr_low = qa_low / li_low
    qr_high = qa_high / li_high
    avg_ratio = p_high * qr_high + p_low * qr_low

    exp_qa = p_high * qa_high + p_low * qa_low
    exp_li = p_high * li_high + p_low * li_low
    ratio_of_exp = exp_qa / exp_li

    premium_pp = (avg_ratio - ratio_of_exp) * 100

    return {
        "final": premium_pp,
        "slots": {
            "low_state_retained_cash_checkpoint": cash_low,
            "incremental_retained_cash_checkpoint": cash_high - cash_low,
            "incremental_repayment_checkpoint": repay_high - repay_low,
        },
    }
