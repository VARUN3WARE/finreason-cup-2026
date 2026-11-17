from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h083"


def solve(text: str, q: dict) -> dict:
    n1, p1, n2, p2 = grab_all(
        r"owns {N} shares bought at {N} per share and {N} shares bought at {N} per share", text
    )
    p0 = grab(r"selling the complete position now at {N} per share", text)
    c0 = grab(r"position now at {N} per share with total sale cost {N}", text, group=2)
    pb = grab(r"base terminal sale price is {N}", text)
    pd = grab(r"downside terminal sale price is {N}", text)
    div = grab(r"gross terminal dividend is {N} per share", text)
    c1 = grab(r"total future sale cost is {N}", text)
    tg = grab(r"gain tax ratio {N}", text)
    td = grab(r"[Tt]erminal dividend tax ratio is {N}", text)
    r = grab(r"time-value-only rate {N}", text)
    qd = grab(r"downside probability {N}", text)
    floor_now = grab(r"Current sale qualifies when its exact after-tax cash is at least {N}", text)
    floor_hold = grab(r"Holding qualifies when exact downside-state present value is at least {N}", text)

    shares = n1 + n2
    basis = n1 * p1 + n2 * p2

    def sale(price, cost):
        realized = shares * price - cost
        gain = realized - basis
        taxable = gain if gain > 0 else Fraction(0)  # no loss credit
        return taxable, realized - tg * taxable

    g0, cash0 = sale(p0, c0)
    div_net = shares * div * (1 - td)

    gb, sale_b = sale(pb, c1)
    gd, sale_d = sale(pd, c1)
    pv_b = (sale_b + div_net) / (1 + r)
    pv_d = (sale_d + div_net) / (1 + r)
    ev_hold = qd * pv_d + (1 - qd) * pv_b

    now_ok = cash0 >= floor_now
    hold_ok = pv_d >= floor_hold
    if now_ok and hold_ok:
        final = "Current sale" if cash0 >= ev_hold else "Hold then sell"
    elif now_ok:
        final = "Current sale"
    elif hold_ok:
        final = "Hold then sell"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "current_gain_checkpoint": g0,
            "base_gain_checkpoint": gb,
            "downside_gain_checkpoint": gd,
        },
    }
