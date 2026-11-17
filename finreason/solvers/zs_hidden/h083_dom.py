# FINANCE MODEL (h083): sell-now vs hold-one-period decision with lot basis, gain tax, dividend tax.
#
# Position: lots (n1 @ c1) and (n2 @ c2). N = n1 + n2 shares. Complete two-lot basis B = n1*c1 + n2*c2.
#
# Current sale (time 0):
#   AR_now   = N * P_now - cost_now                      (sale cost reduces amount realized)
#   gain_now = AR_now - B ; taxable gain = max(gain_now, 0)   (no loss credit; tax only on positive gain)
#   tax_now  = t_gain * taxable_gain
#   cash_now = AR_now - tax_now                          (exact after-tax cash, total USD)
#
# Hold one period, state s in {base, downside}:
#   AR_s     = N * P_s - cost_future
#   gain_s   = AR_s - B ; taxable gain_s = max(gain_s, 0)  (same two-lot basis; positive gain only)
#   div_net  = N * d * (1 - t_div)                       (dividend taxed at its own ratio, not as gain)
#   cash_s   = AR_s - t_gain * taxable_gain_s + div_net  (after-tax cash at terminal time)
#   PV_s     = cash_s / (1 + r)                          (one period, time-value-only rate, no risk premium)
#   Probabilities: downside q, base 1 - q.  E[PV] = q*PV_down + (1-q)*PV_base.
#
# Decision:
#   current qualifies  iff cash_now >= floor_now          (at least: >=)
#   hold qualifies     iff PV_down >= floor_hold          (at least: >=)
#   both qualify -> higher of cash_now vs E[PV]; exact tie -> "Current sale"
#   only one qualifies -> that one; none -> "Neither".
#
# Checkpoints (unrounded; framework rounds half-up to cents): taxable gains (positive-part) for
# current sale, base state, downside state. Overrides: none beyond the text's scenario-local rules.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h083"


def solve(text: str, q: dict) -> dict:
    n1, c1 = grab_all(r"owns {N} shares bought at {N} per share", text)
    n2, c2 = grab_all(r"and {N} shares bought at {N} per share", text)
    p_now = grab(r"now at {N} per share", text)
    cost_now = grab(r"with total sale cost {N}", text)
    p_base = grab(r"base terminal sale price is {N}", text)
    p_down = grab(r"downside terminal sale price is {N}", text)
    div = grab(r"gross terminal dividend is {N} per share", text)
    cost_fut = grab(r"total future sale cost is {N}", text)
    t_gain = grab(r"gain tax ratio {N}", text)
    t_div = grab(r"Terminal dividend tax ratio is {N}", text)
    rate = grab(r"time-value-only rate {N}", text)
    q_down = grab(r"downside probability {N}", text)
    floor_now = grab(r"Current sale qualifies when its exact after-tax cash is at least {N}", text)
    floor_hold = grab(r"exact downside-state present value is at least {N}", text)

    N = n1 + n2
    B = n1 * c1 + n2 * c2

    def pos(x):
        return x if x > 0 else Fraction(0)

    ar_now = N * p_now - cost_now
    gain_now = pos(ar_now - B)
    cash_now = ar_now - t_gain * gain_now

    div_net = N * div * (1 - t_div)

    def hold_state(price):
        ar = N * price - cost_fut
        g = pos(ar - B)
        cash = ar - t_gain * g + div_net
        return g, cash / (1 + rate)

    g_base, pv_base = hold_state(p_base)
    g_down, pv_down = hold_state(p_down)
    ev = q_down * pv_down + (1 - q_down) * pv_base

    cur_ok = cash_now >= floor_now
    hold_ok = pv_down >= floor_hold
    if cur_ok and hold_ok:
        final = "Hold then sell" if ev > cash_now else "Current sale"
    elif cur_ok:
        final = "Current sale"
    elif hold_ok:
        final = "Hold then sell"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "current_gain_checkpoint": gain_now,
            "base_gain_checkpoint": g_base,
            "downside_gain_checkpoint": g_down,
        },
    }
