# FINANCE MODEL (h051)
# Two-state (bull / bear) subjective model; one-unit cash-settled vanilla European options, same underlying/expiry.
#   S_u = bullish terminal price, S_d = bearish terminal price (S_d < S_u), p = bullish probability, q = 1 - p.
#   Strikes K_c, K_p both lie strictly between S_d and S_u.
#   Call payoff:  bull = max(S_u - K_c, 0) = S_u - K_c (>0);  bear = max(S_d - K_c, 0) = 0.
#   Put payoff:   bull = max(K_p - S_u, 0) = 0;               bear = max(K_p - S_d, 0) = K_p - S_d (>0).
#   Profit per state = payoff - premium (premium subtracted ONCE, undiscounted, no financing/dividends/costs).
#   Expected profit  = p*payoff_bull + q*payoff_bear - premium (exact, Fractions).
#   Worst-state profit = min over the two states of (payoff - premium).
#   A strategy qualifies iff expected profit >= E_min (inclusive, "at least") AND worst-state profit >= W_min
#   (inclusive; W_min is negative, e.g. -11).
#   Decision: among qualifying strategies pick the higher expected profit; exact tie -> "Call"; none -> "Neither".
#   Checkpoints (unrounded; framework rounds half-up to cents):
#       call_payoff_checkpoint = positive bull-state call payoff = S_u - K_c
#       put_payoff_checkpoint  = positive bear-state put payoff  = K_p - S_d
# No overrides of standard conventions beyond those stated in the text.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h051"


def solve(text: str, q: dict) -> dict:
    s_u = grab(r"bullish terminal price {N}", text)
    s_d = grab(r"bearish terminal price {N}", text)
    p = grab(r"bullish probability {N}", text)
    k_c = grab(r"call with strike {N}", text)
    k_p = grab(r"put with strike {N}", text)
    prem_c = grab(r"call premium {N}", text)
    prem_p = grab(r"put premium {N}", text)
    e_min = grab(r"expected profit is at least {N}", text)
    w_min = grab(r"worst-state profit is at least {N}", text)

    pr_u, pr_d = p, 1 - p

    call_u = max(s_u - k_c, Fraction(0))
    call_d = max(s_d - k_c, Fraction(0))
    put_u = max(k_p - s_u, Fraction(0))
    put_d = max(k_p - s_d, Fraction(0))

    call_e = pr_u * call_u + pr_d * call_d - prem_c
    put_e = pr_u * put_u + pr_d * put_d - prem_p
    call_w = min(call_u, call_d) - prem_c
    put_w = min(put_u, put_d) - prem_p

    call_ok = call_e >= e_min and call_w >= w_min
    put_ok = put_e >= e_min and put_w >= w_min

    if call_ok and put_ok:
        final = "Call" if call_e >= put_e else "Put"
    elif call_ok:
        final = "Call"
    elif put_ok:
        final = "Put"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "call_payoff_checkpoint": call_u,
            "put_payoff_checkpoint": put_d,
        },
    }
