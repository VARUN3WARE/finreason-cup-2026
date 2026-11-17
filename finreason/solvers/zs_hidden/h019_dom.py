"""h019 -- maximum common stress activity x allowed by capital / leverage / liquidity constraints.

FINANCE MODEL (written before coding)
-------------------------------------
Balance-sheet items (USD millions) under a single dimensionless stress activity x >= 0:
    eligible capital   E(x) = E0 - a_E * x
    Tier 1 capital     T(x) = T0 - a_T * x
    risk-weighted assets R(x) = R0 + a_R * x
    total exposure     X(x) = X0 + a_X * x
    HQLA               H(x) = H0 - a_H * x
    net cash outflows  O(x) = O0 + a_O * x
Each coefficient a_* is the USD-million adverse change per unit of x (given in the text).

Regulatory-style ratio constraints (the scenario is fictional; apply only the stated rule):
    capital ratio    E(x)/R(x) >= k,   k = minimum capital ratio + capital buffer ratio   (decimal ratio)
    leverage ratio   T(x)/X(x) >= minimum leverage ratio
    liquidity (LCR)  H(x)/O(x) >= minimum liquidity ratio
Each is linear in x after cross-multiplying, so the constraint "first binds" (equality) at
    x_cap = (E0 - k*R0) / (a_E + k*a_R)
    x_lev = (T0 - m_lev*X0) / (a_T + m_lev*a_X)
    x_liq = (H0 - m_liq*O0) / (a_H + m_liq*a_O)
which are exactly the three formulas stated in the text.
Maximum common stress activity (final answer, "multiple", half-up 2 dp) = min(x_cap, x_lev, x_liq).
Checkpoint: k = min capital ratio + buffer ratio, kept exact/unrounded downstream (reported to 6 dp, ratio).

Conventions / ambiguities resolved
  * Ratios are decimal ratios (0.1 = 10%), k is a plain ratio (not percent).
  * The text says "return the smallest of the three capacities" with no floor at zero, so the
    literal min of the three formulas is returned (a constraint already breached at x = 0 gives a
    negative capacity, which is then the minimum; no max(0, .) is applied).
  * All arithmetic exact with Fraction; no intermediate rounding (k unrounded downstream).
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h019"


def solve(text: str, q: dict) -> dict:
    E0 = grab(r"begins with eligible capital {N}", text)
    T0 = grab(r"Tier 1 capital {N}, risk-weighted assets", text)
    R0 = grab(r"risk-weighted assets {N}, total exposure", text)
    X0 = grab(r"total exposure {N}, high-quality liquid assets", text)
    H0 = grab(r"high-quality liquid assets {N}, and total net cash outflows", text)
    O0 = grab(r"total net cash outflows {N}, all in USD millions", text)

    m_cap = grab(r"minimum capital ratio {N}", text)
    buf = grab(r"capital buffer ratio {N}", text)
    m_lev = grab(r"minimum leverage ratio {N}", text)
    m_liq = grab(r"minimum liquidity ratio {N}", text)

    aE = grab(r"decreases eligible capital by {N}\*x", text)
    aT = grab(r"Tier 1 capital by {N}\*x", text)
    aR = grab(r"increasing risk-weighted assets by {N}\*x", text)
    aX = grab(r"exposure by {N}\*x, reducing HQLA", text)
    aH = grab(r"reducing HQLA by {N}\*x", text)
    aO = grab(r"increasing net cash outflows by {N}\*x", text)

    k = m_cap + buf

    x_cap = (E0 - k * R0) / (aE + k * aR)
    x_lev = (T0 - m_lev * X0) / (aT + m_lev * aX)
    x_liq = (H0 - m_liq * O0) / (aH + m_liq * aO)

    final = min(x_cap, x_lev, x_liq)

    return {
        "final": final,
        "slots": {"combined_capital_requirement_ratio_checkpoint": k},
    }
