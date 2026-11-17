"""h025 -- minimum gross terminal salvage under an expected-NPV floor and a stressed-NPV floor.

STRUCTURE
    cost C at t=0; interim cash flow I at year n1; terminal net flow (S - K) at year n2
    (gross salvage S received together with cleanup cost K, same S and K in both scenarios).
    Two scenarios: stress (prob p, rate r_s) and normal (prob 1-p, rate r_n).
    Conditional NPV_j = -C + I/(1+r_j)^n1 + (S - K)/(1+r_j)^n2        (no probabilities inside)
    Expected NPV     = p*NPV_s + (1-p)*NPV_n                            (decision-analysis expectation)
    Question: minimum S such that  E[NPV] >= T1  AND  NPV_s >= T2.

AMBIGUITIES CONSIDERED AND RESOLUTIONS
 1. Rates "0.25" / "0.1" are given as plain ratios, not percent ("effective annual discount rate 0.25").
    -> used as ratios. Defensive: if the word "percent" follows the rate, divide by 100.
 2. "Compound each rate over the applicable whole-year horizon" -> discount factor (1+r)^n with integer n,
    exact Fraction power; no continuous compounding, no mid-year convention.
 3. Cleanup is "paid ... together with salvage after n2 whole years" -> both at year n2; net flow S - K,
    discounted once by (1+r)^n2. Cleanup is a cost (negative), salvage an inflow (positive).
 4. "Conditional scenario NPVs do not include scenario probabilities" -> NPV_s and NPV_n are plain
    scenario NPVs; probabilities appear only in E[NPV] = p*NPV_s + (1-p)*NPV_n.
 5. Normal probability = "one minus that probability" -> 1 - p (parsed numerically if ever stated).
 6. "at least" for both floors -> non-strict (>=). Both NPVs are continuous, strictly increasing, linear in S,
    so the minimum S satisfying both is the max of the two equality solutions:
       S1 = K + (T1 + C - [p*I/(1+r_s)^n1 + (1-p)*I/(1+r_n)^n1]) / [p/(1+r_s)^n2 + (1-p)/(1+r_n)^n2]
       S2 = K + (T2 + C - I/(1+r_s)^n1) * (1+r_s)^n2
       S* = max(S1, S2).   Either constraint may bind; both are evaluated on every instance.
 7. Thresholds such as "37729209/29282 USD" are exact rationals -> parsed via nums.F (handles a/b).
 8. No floor at zero on S: the question asks for the minimum salvage that satisfies the floors; nothing in
    the text says salvage cannot be negative, and in practice all computed S are large positive values.
    (If it were negative the "minimum" would still be the mathematical boundary, as worded.)
 9. Checkpoints: "conditional interim present value under normal/stress discounting" = the present value
    of the INTERIM cash flow alone, I/(1+r)^n1, under that scenario's rate, unweighted by probability
    ("conditional" = scenario-specific, no probability), in USD, unrounded.
10. Interim year n1 may be before or after the terminal year n2 (instance 2 has n1 > n2); formula is
    unaffected.
11. Everything returned unrounded; framework rounds half-up to 2 dp.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab, grab_all, F

TEMPLATE_ID = "h025"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate; convert from percent to ratio only if 'percent'/'%' immediately follows."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    val = F(m.group(1))
    tail = text[m.end(1): m.end(1) + 10]
    if re.match(r"\s*(percent|%)", tail):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    # --- cash flows and timings
    cost = grab(r"costs\s+{N}\s+USD\s+now", text)
    interim, n_interim = grab_all(
        r"interim cash flow of\s+{N}\s+USD\s+after\s+{N}\s+whole years", text
    )
    cleanup, n_terminal = grab_all(
        r"cleanup cost\s+{N}\s+USD\s+together with salvage after\s+{N}\s+whole years", text
    )
    n1 = int(n_interim)
    n2 = int(n_terminal)
    assert Fraction(n1) == n_interim and Fraction(n2) == n_terminal, "whole-year horizons expected"

    # --- scenarios
    p_stress = grab(r"stress scenario has probability\s+{N}", text)
    r_stress = _rate(
        r"stress scenario has probability\s+" + NUMBER + r"\s+and effective annual discount rate\s+{N}",
        text,
    )
    # normal probability: "one minus that probability" (or a number if ever stated explicitly)
    m_pn = re.search(r"normal scenario has probability\s+(" + NUMBER + r")", text)
    if m_pn:
        p_normal = F(m_pn.group(1))
    else:
        assert "one minus that probability" in text
        p_normal = 1 - p_stress
    r_normal = _rate(r"normal scenario has probability.*?effective annual discount rate\s+{N}", text)

    # --- thresholds
    t_expected = grab(r"expected NPV at least\s+{N}\s+USD", text)
    t_stress = grab(r"stressed-scenario NPV at least\s+{N}\s+USD", text)

    # --- discount factors (exact integer powers)
    df_s1 = 1 / (1 + r_stress) ** n1
    df_s2 = 1 / (1 + r_stress) ** n2
    df_n1 = 1 / (1 + r_normal) ** n1
    df_n2 = 1 / (1 + r_normal) ** n2

    # --- conditional interim present values (checkpoints)
    pv_interim_normal = interim * df_n1
    pv_interim_stress = interim * df_s1

    # --- salvage that makes the stressed NPV exactly T2:  -C + PV_I_s + (S-K)*df_s2 = T2
    s_from_stress = cleanup + (t_stress + cost - pv_interim_stress) / df_s2

    # --- salvage that makes the expected NPV exactly T1
    exp_pv_interim = p_stress * pv_interim_stress + p_normal * pv_interim_normal
    exp_df_terminal = p_stress * df_s2 + p_normal * df_n2
    s_from_expected = cleanup + (t_expected + cost - exp_pv_interim) / exp_df_terminal

    # both floors must hold ("at least" -> >=); NPVs increase in S, so take the larger boundary
    salvage_min = max(s_from_expected, s_from_stress)

    # sanity: verify both constraints hold with equality on the binding one
    npv_s = -cost + pv_interim_stress + (salvage_min - cleanup) * df_s2
    npv_n = -cost + pv_interim_normal + (salvage_min - cleanup) * df_n2
    enpv = p_stress * npv_s + p_normal * npv_n
    assert npv_s >= t_stress and enpv >= t_expected
    assert npv_s == t_stress or enpv == t_expected

    return {
        "final": salvage_min,
        "slots": {
            "normal_interim_present_value_checkpoint": pv_interim_normal,
            "stressed_interim_present_value_checkpoint": pv_interim_stress,
        },
    }
