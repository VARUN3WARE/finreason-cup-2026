"""Hidden cluster h002 -- loss-severity alignment diagnostic (state-specific vs flat-rate reimbursement).

Structure
---------
Conditional on one fraud event, exactly one of three mutually exclusive, exhaustive loss states
occurs (minor / moderate / severe). Probabilities are given as a chain:
    P(first-named state)             = p_a                         (e.g. minor, 0.2)
    P(second state | not first)      = q                           (e.g. moderate, 0.5)
    P(third state  | not first)      = 1 - q                       ("otherwise ... occurs")
so P(second) = (1 - p_a) * q and P(third) = (1 - p_a) * (1 - q).

    actual expected reimbursement   E[R]  = sum_i p_i * L_i * r_i
    probability-weighted mean rate  rbar  = sum_i p_i * r_i          (/ sum_i p_i, which is 1)
    expected gross loss             E[L]  = sum_i p_i * L_i
    flat-rate benchmark             B     = rbar * E[L]
    final                           E[R] - B                        (USD, exact; framework rounds 2dp half-up)

Checkpoints
-----------
    moderate_weighted_loss_checkpoint = P(moderate) * L_moderate   (gross loss, before reimbursement, USD)
    severe_weighted_loss_checkpoint   = P(severe)   * L_severe     (gross loss, before reimbursement, USD)

Ambiguities hunted and how each was resolved
--------------------------------------------
A1. "probability-weighted mean reimbursement rate": weight the three REIMBURSEMENT FRACTIONS by the
    state PROBABILITIES (sum p_i r_i), not by expected loss (E[R]/E[L]).  Evidence: the text says
    "probability-weighted" explicitly; a loss-weighted mean would make B == E[R] identically and the
    diagnostic would be zero for every instance, contradicting the "positive means ... / negative means
    ..." interpretation paragraph.  Mathematically the result is then Cov_p(r, L), which is exactly the
    stated sign semantics (positive <=> higher rates sit on higher-loss states).
A2. State probabilities: the moderate 0.5 is CONDITIONAL on the minor state not occurring, so
    P(moderate) = (1 - 0.2) * 0.5 = 0.4, not 0.5; P(severe) = (1 - 0.2) * (1 - 0.5) = 0.4 ("otherwise the
    severe state occurs" = the remaining conditional mass).  Probabilities are decimals (0.2), not percents;
    a trailing "percent" is handled defensively but is absent in all visible instances.
A3. Ordering of the loss list and the fraction list: "Their gross fraud losses are a, b, and c" and
    "reimburses fractions x, y, and z" follow the order in which the states were introduced
    (minor, moderate, severe).  Visible instances also show strictly increasing losses, consistent
    with minor < moderate < severe.  Each state's probability is attached by NAME, so a swapped
    conditional clause (e.g. severe named in the conditional, moderate as the "otherwise") still maps
    correctly.
A4. "Expected gross loss" is E[L] = sum p_i L_i, the expectation across the three states given the
    fraud event (the whole scenario is already conditional on one event; no further scaling).
A5. The checkpoints are GROSS losses weighted by probability (p_i * L_i), NOT reimbursements
    (p_i * L_i * r_i) and NOT benchmark pieces.  Slot descriptions say "probability-weighted
    moderate-state gross loss" / "... severe-state gross loss", unit usd.
A6. Sign/order of subtraction: "actual expected reimbursement minus that benchmark" => E[R] - B.
A7. Rounding: no intermediate rounding anywhere ("use exact arithmetic"); only the framework rounds the
    final (2dp) and the checkpoints (4dp) half-up.  All values returned exact.
A8. Units: losses are USD, fractions are plain ratios (0.35 means 35%), result in USD.  No percent
    conversions needed except the defensive handling in A2.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, NUMBER, grab

TEMPLATE_ID = "h002"

STATES = ("minor", "moderate", "severe")


def _prob(num_text: str, pct: str | None) -> Fraction:
    p = F(num_text)
    if pct:
        p = p / 100
    return p


def _state_probabilities(text: str) -> dict[str, Fraction]:
    """Attach a probability to each named state from the conditional chain."""
    # First-named unconditional state: "The minor state has probability 0.2."
    m_first = re.search(
        rf"[Tt]he (minor|moderate|severe) state has probability ({NUMBER})\s*(percent|%)?",
        text,
    )
    if m_first is None:
        raise ValueError("unconditional state probability not found")
    first = m_first.group(1)
    p_first = _prob(m_first.group(2), m_first.group(3))

    # Conditional clause: "Conditional on the minor state not occurring, the moderate state has
    # probability 0.5; otherwise the severe state occurs."
    m_cond = re.search(
        rf"[Cc]onditional on the (minor|moderate|severe) state not occurring,\s*"
        rf"the (minor|moderate|severe) state has probability ({NUMBER})\s*(percent|%)?"
        rf"[;,.]?\s*otherwise,?\s*the (minor|moderate|severe) state occurs",
        text,
    )
    if m_cond is None:
        raise ValueError("conditional state probability clause not found")
    cond_on, second, third = m_cond.group(1), m_cond.group(2), m_cond.group(5)
    if cond_on != first:
        raise ValueError(f"conditional clause conditions on {cond_on!r} but first state is {first!r}")
    if len({first, second, third}) != 3:
        raise ValueError("state names in probability chain are not distinct")
    q = _prob(m_cond.group(3), m_cond.group(4))

    probs = {
        first: p_first,
        second: (1 - p_first) * q,
        third: (1 - p_first) * (1 - q),
    }
    if sum(probs.values()) != 1:
        raise ValueError(f"state probabilities do not sum to one: {probs}")
    return probs


def _triple(pattern: str, text: str) -> list[Fraction]:
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    return [F(g) for g in m.groups()]


def solve(text: str, q: dict) -> dict:
    probs = _state_probabilities(text)

    # Lists follow the introduction order minor, moderate, severe (A3).
    losses = _triple(r"gross (?:fraud )?losses are {N},\s*{N},?\s*and {N}\s*USD", text)
    rates = _triple(r"reimburses fractions {N},\s*{N},?\s*and {N}", text)

    L = dict(zip(STATES, losses))
    r = dict(zip(STATES, rates))
    p = {s: probs[s] for s in STATES}

    total_p = sum(p.values())  # == 1 (exhaustive states); kept for clarity of the weighted mean

    # Probability-weighted gross losses (checkpoints) and expected gross loss.
    weighted_loss = {s: p[s] * L[s] for s in STATES}
    expected_gross_loss = sum(weighted_loss.values())

    # Actual expected reimbursement across the three states.
    actual_expected_reimb = sum(p[s] * L[s] * r[s] for s in STATES)

    # Scenario-specific flat-rate benchmark: probability-weighted mean rate applied to expected gross loss.
    mean_rate = sum(p[s] * r[s] for s in STATES) / total_p
    benchmark = mean_rate * expected_gross_loss

    final = actual_expected_reimb - benchmark

    return {
        "final": final,
        "slots": {
            "moderate_weighted_loss_checkpoint": weighted_loss["moderate"],
            "severe_weighted_loss_checkpoint": weighted_loss["severe"],
        },
    }
