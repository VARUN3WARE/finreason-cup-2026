"""h081 -- two-strategy allocation: feasible weight interval from upside/downturn floors,
endpoint chosen by comparing all-A vs all-B probability-weighted ending values.
Literal sentence-by-sentence transcription."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h081"


def solve(text: str, q: dict) -> dict:
    # S1: "An investor allocates weight w of capital C to Strategy A and the complementary weight to Strategy B."
    capital = grab(r"weight w of capital {N} to Strategy A", text)

    # S2: "The downturn probability is p, with the complementary probability assigned to the upside scenario."
    p_down = grab(r"downturn probability is {N}", text)
    p_up = 1 - p_down

    # S3: "Strategy B earns upside return rB and loses lB in the downturn."
    b_up_ret = grab(r"Strategy B earns upside return {N}", text)
    b_down_loss = grab(r"and loses {N} in the downturn", text)

    # S4: "Strategy A earns the B upside return plus positive incremental return dU, but loses the B
    #      downturn loss plus positive incremental loss dL; both resulting Strategy A rates remain below one."
    inc_ret = grab(r"positive incremental return {N}", text)
    inc_loss = grab(r"positive incremental loss {N}", text)
    a_up_ret = b_up_ret + inc_ret
    a_down_loss = b_down_loss + inc_loss

    # Gross ending multipliers per unit of capital in each scenario.
    a_up_gross = 1 + a_up_ret
    a_down_gross = 1 - a_down_loss
    b_up_gross = 1 + b_up_ret
    b_down_gross = 1 - b_down_loss

    # S5: "The portfolio must end with at least U in the upside scenario and at least D in the downturn."
    req_up = grab(r"at least {N} in the upside scenario", text)
    req_down = grab(r"at least {N} in the downturn", text)

    # S6/S7: linear weighted combinations, no interaction/leverage/fees/rebalancing.
    #   upside:   C*(w*a_up_gross + (1-w)*b_up_gross)     >= U  -> w >= lower (A beats B in upside)
    #   downturn: C*(w*a_down_gross + (1-w)*b_down_gross) >= D  -> w <= upper (A worse in downturn)
    # Upside requirement supplies the lower endpoint, downturn requirement supplies the upper endpoint.
    lower = (req_up / capital - b_up_gross) / (a_up_gross - b_up_gross)
    upper = (req_down / capital - b_down_gross) / (a_down_gross - b_down_gross)

    # Determine feasibility (text guarantees a nonempty interval strictly inside (0, 1)).
    feasible = (lower <= upper) and (0 < lower) and (upper < 1)
    _ = feasible  # stated as guaranteed; selection proceeds with exact endpoints regardless

    # S8: compare exact probability-weighted ending values of all-A vs all-B.
    a_upside_end = capital * a_up_gross
    a_downturn_end = capital * a_down_gross
    b_upside_end = capital * b_up_gross
    b_downturn_end = capital * b_down_gross

    a_weighted_upside = p_up * a_upside_end
    a_weighted_downturn = p_down * a_downturn_end
    ev_all_a = a_weighted_upside + a_weighted_downturn
    ev_all_b = p_up * b_upside_end + p_down * b_downturn_end

    # Strictly greater -> upper endpoint; otherwise (incl. exact tie) -> lower endpoint.
    w_sel = upper if ev_all_a > ev_all_b else lower

    final = w_sel * 100  # percent

    return {
        "final": final,
        "slots": {
            "strategy_a_weighted_upside_checkpoint": a_weighted_upside,
            "strategy_b_downturn_checkpoint": b_downturn_end,
        },
    }
