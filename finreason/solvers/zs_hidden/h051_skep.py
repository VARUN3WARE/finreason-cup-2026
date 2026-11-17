"""h051 -- one-unit vanilla call vs put under two exhaustive subjective scenarios.

AMBIGUITY RESOLUTIONS (skeptical pass; every point two analysts could split on):

1. Checkpoints are PAYOFFS, not profits.
   Slot descriptions say "positive bull-state call payoff" / "positive bear-state put payoff".
   The text separates "pays its bull-state intrinsic value" (payoff) from "profit" (after
   subtracting the premium).  So call_payoff_checkpoint = S_bull - K_call and
   put_payoff_checkpoint = K_put - S_bear, with NO premium subtracted.  "Each generated strike
   lies strictly between the two prices" guarantees both are strictly positive, matching the
   word "positive" in the slot descriptions.

2. Premium is subtracted ONCE, unweighted, from the probability-weighted payoff:
   "Subtract call premium ... once from their respective probability-weighted payoffs".
   E[profit_call] = p * (S_bull - K_call) - c ;  E[profit_put] = (1 - p) * (K_put - S_bear) - q.
   (NOT p * (payoff - premium), which would weight the premium by p.)

3. Bear probability = 1 - p.  "exhaustive subjective scenarios" -> the two states partition
   the probability space.  Probability is given as a decimal (0.6), not a percent; a defensive
   divide-by-100 is applied only if the parsed value exceeds 1, which never triggers here.

4. "exact worst-state profit" = the profit in whichever state yields the lower profit, i.e.
   min over states of (state payoff - premium).  For the call the bear state pays 0, so the
   worst-state profit is -c; for the put the bull state pays 0, so it is -q.  Computed
   generically as a min over both states rather than hard-wiring -premium.

5. Qualification uses "at least" twice -> both comparisons are >= (non-strict), and BOTH
   conditions must hold ("qualifies only if ... and ...").  The worst-state threshold is a
   signed (negative) number; the NUMBER regex captures the leading minus sign.

6. Selection: among QUALIFYING strategies only, pick the higher exact expected profit;
   exact tie -> "Call"; if exactly one qualifies return it regardless of which has the higher
   expected profit; if none qualify -> "Neither".  Comparison is on exact Fractions.

7. Units: all amounts are USD per share and contracts are one-unit, so no scaling.
   "undiscounted simple terminal profit" -> no discounting, no financing, no dividends,
   no transaction costs: nothing else is subtracted or compounded.

8. Payoffs are computed as max(S - K, 0) / max(K - S, 0) per state so the code matches the
   stated contract definition even though the strict-between-prices guarantee makes the
   zero branches trivially correct here.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h051"


def _call_payoff(s: Fraction, k: Fraction) -> Fraction:
    return max(s - k, Fraction(0))


def _put_payoff(s: Fraction, k: Fraction) -> Fraction:
    return max(k - s, Fraction(0))


def solve(text: str, q: dict) -> dict:
    s_bull = grab(r"bullish terminal price\s+{N}", text)
    s_bear = grab(r"bearish terminal price\s+{N}", text)
    p_bull = grab(r"bullish probability\s+{N}", text)
    if p_bull > 1:  # defensive: a percent-style probability (never the case in these texts)
        p_bull = p_bull / 100
    p_bear = Fraction(1) - p_bull

    k_call = grab(r"call with strike\s+{N}", text)
    k_put = grab(r"put with strike\s+{N}", text)
    prem_call = grab(r"call premium\s+{N}", text)
    prem_put = grab(r"put premium\s+{N}", text)

    min_expected = grab(r"expected profit is at least\s+{N}", text)
    min_worst = grab(r"worst-state profit is at least\s+{N}", text)

    # Per-state payoffs (intrinsic values, no premium).
    call_bull = _call_payoff(s_bull, k_call)
    call_bear = _call_payoff(s_bear, k_call)
    put_bull = _put_payoff(s_bull, k_put)
    put_bear = _put_payoff(s_bear, k_put)

    # Expected profit: probability-weighted payoff minus premium subtracted once.
    exp_call = p_bull * call_bull + p_bear * call_bear - prem_call
    exp_put = p_bull * put_bull + p_bear * put_bear - prem_put

    # Worst-state profit: lowest state profit (payoff minus premium in that state).
    worst_call = min(call_bull - prem_call, call_bear - prem_call)
    worst_put = min(put_bull - prem_put, put_bear - prem_put)

    call_ok = exp_call >= min_expected and worst_call >= min_worst
    put_ok = exp_put >= min_expected and worst_put >= min_worst

    if call_ok and put_ok:
        final = "Call" if exp_call >= exp_put else "Put"  # exact tie -> Call
    elif call_ok:
        final = "Call"
    elif put_ok:
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
