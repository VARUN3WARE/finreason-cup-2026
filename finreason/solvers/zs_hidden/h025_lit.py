"""h025 -- literal transcription solver.

Two-scenario (stress / normal) project NPV with interim cash flow and a terminal
date carrying cleanup cost plus gross salvage; find the minimum gross terminal
salvage meeting an expected-NPV floor and a stressed-scenario NPV floor.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h025"


def solve(text: str, q: dict) -> dict:
    # S1: "A project costs C0 USD now, produces an interim cash flow of I USD after t1 whole years,
    #      and pays cleanup cost K USD together with salvage after t2 whole years."
    c0 = grab(r"project costs {N} USD now", text)
    interim = grab(r"interim cash flow of {N} USD after", text)
    t_interim = grab(r"interim cash flow of [^ ]+ USD after {N} whole years", text)
    cleanup = grab(r"cleanup cost {N} USD", text)
    t_terminal = grab(r"together with salvage after {N} whole years", text)
    assert t_interim.denominator == 1 and t_terminal.denominator == 1
    t_interim = int(t_interim)
    t_terminal = int(t_terminal)

    # S2: "The same gross salvage and cleanup apply in both scenarios." -> one S, one K.

    # S3: stress probability p and rate; normal probability 1 - p and rate.
    p_stress = grab(r"stress scenario has probability {N}", text)
    r_stress = grab(r"stress scenario has probability [^ ]+ and effective annual discount rate {N}", text)
    p_normal = 1 - p_stress
    r_normal = grab(r"normal scenario has probability one minus that probability and effective annual discount rate {N}", text)

    # S4: "Compound each rate over the applicable whole-year horizon."
    def df(rate: Fraction, years: int) -> Fraction:
        return 1 / (1 + rate) ** years

    # Checkpoints: conditional interim present values (no probabilities).
    pv_interim_normal = interim * df(r_normal, t_interim)
    pv_interim_stress = interim * df(r_stress, t_interim)

    # S5: conditional scenario NPVs (no probabilities), as linear functions of gross salvage S:
    #     NPV_s(S) = -C0 + I*df(r_s,t1) + (S - K)*df(r_s,t2) = a_s + b_s * S
    def npv_parts(rate: Fraction, pv_int: Fraction):
        d_term = df(rate, t_terminal)
        a = -c0 + pv_int - cleanup * d_term
        b = d_term
        return a, b

    a_n, b_n = npv_parts(r_normal, pv_interim_normal)
    a_s, b_s = npv_parts(r_stress, pv_interim_stress)

    # S6: Expected NPV = p_stress * NPV_stress + p_normal * NPV_normal.
    a_e = p_stress * a_s + p_normal * a_n
    b_e = p_stress * b_s + p_normal * b_n

    # Question: minimum gross salvage with E[NPV] >= target_e and NPV_stress >= target_s.
    target_e = grab(r"expected NPV at least {N} USD", text)
    target_s = grab(r"stressed-scenario NPV at least {N} USD", text)

    s_req_expected = (target_e - a_e) / b_e
    s_req_stress = (target_s - a_s) / b_s
    s_min = max(s_req_expected, s_req_stress)

    return {
        "final": s_min,
        "slots": {
            "normal_interim_present_value_checkpoint": pv_interim_normal,
            "stressed_interim_present_value_checkpoint": pv_interim_stress,
        },
    }
