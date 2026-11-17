"""h025 -- minimum gross terminal salvage under a two-scenario (normal / stress) NPV test.

FINANCE MODEL (written before coding)
-------------------------------------
Project cash flows (identical in both scenarios, only the discount rate differs):
    t = 0   : -I0                       (initial cost, no discounting)
    t = t1  : +C                        (interim cash flow, whole years)
    t = t2  : +S - K                    (gross terminal salvage S, less cleanup cost K, both paid
                                         together at the terminal date t2; t2 may be EARLIER or
                                         LATER than t1 -- each flow is discounted by its own date)
Scenarios (rate = effective annual rate, discount factor for horizon t is (1+r)**(-t), integer t):
    stress : probability p, rate r_s
    normal : probability 1-p, rate r_n
Conditional scenario NPV_j = -I0 + C/(1+r_j)^t1 + (S-K)/(1+r_j)^t2   (no probability inside it).
Expected NPV = (1-p)*NPV_normal + p*NPV_stress  (plain probability-weighted decision-analysis mean).

Decision question: smallest gross salvage S such that BOTH
    (a) Expected NPV   >= X
    (b) Stressed NPV   >= Y
Both NPVs are strictly increasing and linear in S, so each constraint gives a lower bound on S;
the minimum S satisfying both is the larger of the two bounds:
    (a) S_a = K + (X + I0 - E[PV interim]) / E[discount factor at t2]
        with E[PV interim] = (1-p)*C/(1+r_n)^t1 + p*C/(1+r_s)^t1 and
             E[df(t2)]     = (1-p)/(1+r_n)^t2  + p/(1+r_s)^t2
    (b) S_b = K + (Y + I0 - C/(1+r_s)^t1) * (1+r_s)^t2
    S*  = max(S_a, S_b)         (the bound that binds is whichever is larger; no extra floor at 0
                                 since none is stated -- and S* is large and positive in practice)
Checkpoints (conditional, i.e. NOT probability-weighted, and only the interim leg):
    normal_interim_present_value_checkpoint   = C / (1+r_n)^t1
    stressed_interim_present_value_checkpoint = C / (1+r_s)^t1
Final answer unit: USD, rounded half-up to 2 dp by the framework (all arithmetic exact Fractions).

Overrides / notes: rates are given as decimals (0.25 = 25%), NOT percent. Probability of the
normal scenario is 1 - p_stress. No rounding is applied anywhere inside the computation.
"""
from fractions import Fraction

from finreason.nums import grab, grab_all, F  # noqa: F401

TEMPLATE_ID = "h025"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs {N} USD now", text)
    c, t1 = grab_all(r"interim cash flow of {N} USD after {N} whole years", text)
    k, t2 = grab_all(r"cleanup cost {N} USD together with salvage after {N} whole years", text)
    p, r_s = grab_all(
        r"stress scenario has probability {N} and effective annual discount rate {N}", text
    )
    r_n = grab(
        r"normal scenario has probability one minus that probability and effective annual "
        r"discount rate {N}",
        text,
    )
    x, y = grab_all(
        r"expected NPV at least {N} USD and stressed-scenario NPV at least {N} USD", text
    )

    t1 = int(t1)
    t2 = int(t2)
    one = Fraction(1)

    pv_int_n = c / (one + r_n) ** t1
    pv_int_s = c / (one + r_s) ** t1

    e_pv_int = (one - p) * pv_int_n + p * pv_int_s
    e_df_t2 = (one - p) / (one + r_n) ** t2 + p / (one + r_s) ** t2

    # (a) expected-NPV bound
    s_a = k + (x + i0 - e_pv_int) / e_df_t2
    # (b) stressed-NPV bound
    s_b = k + (y + i0 - pv_int_s) * (one + r_s) ** t2

    final = max(s_a, s_b)

    return {
        "final": final,
        "slots": {
            "normal_interim_present_value_checkpoint": pv_int_n,
            "stressed_interim_present_value_checkpoint": pv_int_s,
        },
    }
