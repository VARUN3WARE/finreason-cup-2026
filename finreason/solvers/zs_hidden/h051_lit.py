"""h051 -- literal transcription: one-unit cash-settled call vs put under a two-state
subjective scenario; qualify on expected profit and worst-state profit thresholds."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h051"


def solve(text: str, q: dict) -> dict:
    # "bullish terminal price {S_u} and lower bearish terminal price {S_d}"
    s_bull = grab(r"bullish terminal price {N}", text)
    s_bear = grab(r"bearish terminal price {N}", text)
    # "with bullish probability {p}" -- exhaustive scenarios => bear prob = 1 - p
    p_bull = grab(r"bullish probability {N}", text)
    if "%" in text.split("bullish probability", 1)[1][:20] or "percent" in text.split("bullish probability", 1)[1][:30]:
        p_bull = p_bull / 100
    p_bear = 1 - p_bull

    # "the call with strike {Kc}" / "the put with strike {Kp}"
    k_call = grab(r"call with strike {N}", text)
    k_put = grab(r"put with strike {N}", text)

    # "call premium {c}" / "put premium {pp}"
    prem_call = grab(r"call premium {N}", text)
    prem_put = grab(r"put premium {N}", text)

    # "expected profit is at least {E}" and "worst-state profit is at least {W}"
    min_expected = grab(r"expected profit is at least {N}", text)
    min_worst = grab(r"worst-state profit is at least {N}", text)

    zero = Fraction(0)
    # Vanilla intrinsic values in each state.
    call_pay_bull = max(s_bull - k_call, zero)  # bull-state intrinsic value
    call_pay_bear = max(s_bear - k_call, zero)  # zero (strike above bear price)
    put_pay_bull = max(k_put - s_bull, zero)    # zero (strike below bull price)
    put_pay_bear = max(k_put - s_bear, zero)    # bear-state intrinsic value

    # Subtract premium once from the probability-weighted payoff (undiscounted).
    call_expected = p_bull * call_pay_bull + p_bear * call_pay_bear - prem_call
    put_expected = p_bull * put_pay_bull + p_bear * put_pay_bear - prem_put

    # Worst-state simple terminal profit.
    call_worst = min(call_pay_bull - prem_call, call_pay_bear - prem_call)
    put_worst = min(put_pay_bull - prem_put, put_pay_bear - prem_put)

    call_ok = call_expected >= min_expected and call_worst >= min_worst
    put_ok = put_expected >= min_expected and put_worst >= min_worst

    if call_ok and put_ok:
        final = "Call" if call_expected >= put_expected else "Put"
    elif call_ok:
        final = "Call"
    elif put_ok:
        final = "Put"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "call_payoff_checkpoint": call_pay_bull,
            "put_payoff_checkpoint": put_pay_bear,
        },
    }
