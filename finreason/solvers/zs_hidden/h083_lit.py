"""h083 -- current sale vs one-period hold (two-lot basis, base/downside states), literal transcription."""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h083"


def solve(text: str, q: dict) -> dict:
    # "An investor owns A shares bought at p1 per share and B shares bought at p2 per share."
    n1, p1, n2, p2 = grab_all(
        r"owns {N} shares bought at {N} per share and {N} shares bought at {N} per share", text
    )
    shares = n1 + n2
    # "Compare selling the complete position now at P0 per share with total sale cost C0, ..."
    p_now = grab(r"selling the complete position now at {N} per share", text)
    cost_now = grab(r"now at [^,]*? per share with total sale cost {N}", text)
    # "The base terminal sale price is Pb, the downside terminal sale price is Pd,"
    p_base = grab(r"base terminal sale price is {N}", text)
    p_down = grab(r"downside terminal sale price is {N}", text)
    # "gross terminal dividend is D per share in either state"
    div_ps = grab(r"gross terminal dividend is {N} per share", text)
    # "total future sale cost is C1 in either state"
    cost_future = grab(r"total future sale cost is {N}", text)
    # "gain tax ratio g applies to each generated positive gain"
    gain_tax = grab(r"gain tax ratio {N}", text)
    # "Terminal dividend tax ratio is t."
    div_tax = grab(r"Terminal dividend tax ratio is {N}", text)
    # "Discount both future after-tax cash states one period using time-value-only rate r."
    rate = grab(r"time-value-only rate {N}", text)
    # "Assign subjective downside probability q and base probability one minus that value."
    prob_down = grab(r"subjective downside probability {N}", text)
    prob_base = 1 - prob_down
    # "Current sale qualifies when its exact after-tax cash is at least X."
    cur_floor = grab(r"Current sale qualifies when its exact after-tax cash is at least {N}", text)
    # "Holding qualifies when exact downside-state present value is at least Y."
    hold_floor = grab(r"Holding qualifies when exact downside-state present value is at least {N}", text)

    # complete two-lot basis
    basis = n1 * p1 + n2 * p2

    def sale(price: Fraction, cost: Fraction):
        # sale cost reduces amount realized
        amount_realized = shares * price - cost
        # positive gain equals amount realized minus the complete two-lot basis; no loss credit
        gain = amount_realized - basis
        taxable_gain = gain if gain > 0 else Fraction(0)
        tax = gain_tax * taxable_gain
        return amount_realized, taxable_gain, amount_realized - tax

    # current sale
    _, cur_gain, cur_cash = sale(p_now, cost_now)

    # terminal dividend (gross per share, total position), taxed at the dividend tax ratio
    div_gross = shares * div_ps
    div_after = div_gross * (1 - div_tax)

    # future states
    _, base_gain, base_sale_cash = sale(p_base, cost_future)
    _, down_gain, down_sale_cash = sale(p_down, cost_future)
    base_cash = base_sale_cash + div_after
    down_cash = down_sale_cash + div_after

    disc = 1 + rate
    base_pv = base_cash / disc
    down_pv = down_cash / disc
    hold_value = prob_base * base_pv + prob_down * down_pv

    cur_ok = cur_cash >= cur_floor
    hold_ok = down_pv >= hold_floor

    if cur_ok and hold_ok:
        final = "Current sale" if cur_cash >= hold_value else "Hold then sell"
    elif cur_ok:
        final = "Current sale"
    elif hold_ok:
        final = "Hold then sell"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "current_gain_checkpoint": cur_gain,
            "base_gain_checkpoint": base_gain,
            "downside_gain_checkpoint": down_gain,
        },
    }
