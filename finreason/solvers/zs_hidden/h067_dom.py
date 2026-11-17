# FINANCE MODEL (h067): break-even / target-ROI premium for a cash-settled long call.
#
#   All amounts are USD per underlying share. The call expires in the money.
#   intrinsic payoff   V   = S_T - K                      (stated explicitly; ITM so positive)
#   net settlement     N   = V - fee                      (fee is an ADDITIONAL deduction, separate from K,
#                                                          so K is NOT subtracted twice)
#   simple expiration ROI  = (V - fee - P) / P = N/P - 1  (non-annualized, no financing/discounting)
#   target ratio r         : plain ratio (0.20 == 20%); r = 4 means 400%. NOT percent-divided again.
#
#   Solve ROI(P) = r  ->  N/P - 1 = r  ->  P* = N / (1 + r)       (exact rational).
#   P* is the exact premium threshold; the reported value is the exact P* rounded half-up to cents
#   (framework does the rounding). We do NOT floor to a whole-cent premium (text says the displayed
#   amount is merely a rounded report of the exact threshold).
#
#   Checkpoint "intrinsic_checkpoint" = per-share intrinsic payoff V = S_T - K, unrounded here
#   (framework rounds half-up to cents), i.e. BEFORE the settlement fee is deducted.
#
#   Overrides of standard convention: none (premium paid at t=0, payoff at expiry, no discounting by instruction).

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h067"


def solve(text: str, q: dict) -> dict:
    s_t = grab(r"terminal stock price {N}", text)
    strike = grab(r"strike price {N}", text)
    fee = grab(r"settlement fee {N}", text)
    r = grab(r"target ratio {N}", text)  # plain ratio, 0.20 == 20%

    intrinsic = s_t - strike  # stated: terminal price minus strike (ITM at expiry)
    net = intrinsic - fee  # deduct separate settlement fee
    threshold = net / (1 + r)  # ROI = net/P - 1 = r  ->  P = net/(1+r)

    return {"final": threshold, "slots": {"intrinsic_checkpoint": intrinsic}}
