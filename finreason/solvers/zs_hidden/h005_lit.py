"""h005 -- carbon-credit break-even price vs. internal abatement (literal transcription).

Sentence by sentence:
  1. "Treat one carbon credit as covering one ton of CO2e."
        -> credits needed = tons of planned abatement (1:1).
  2. "A company has internal abatement capacity C tons of CO2e and commits to utilization u."
        -> planned abatement Q = C * u   (checkpoint: planned_abatement_checkpoint, tons_co2e)
  3. "Mobilizing internal abatement costs K USD, plus v USD for each ton internally abated."
        -> internal cost = K + v * Q
  4. "Compute the carbon-credit price in USD per ton of CO2e at which buying credits for the
      same planned abatement quantity costs exactly as much as internal abatement."
        -> P * Q = K + v * Q   =>   P = (K + v * Q) / Q
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h005"


def _utilization(text: str) -> Fraction:
    # "commits to utilization 0.5" (ratio); tolerate a percent phrasing defensively.
    try:
        u = grab(r"utilization(?: of)? {N}\s*(?:percent|%)", text)
        return u / 100
    except ValueError:
        pass
    return grab(r"utilization(?: of)? {N}", text)


def solve(text: str, q: dict) -> dict:
    # Sentence 1: one credit covers one ton of CO2e.
    tons_per_credit = Fraction(1)

    # Sentence 2: capacity and utilization -> planned abatement quantity.
    capacity = grab(r"internal abatement capacity(?: of)? {N} tons", text)
    utilization = _utilization(text)
    planned_abatement = capacity * utilization  # tons CO2e

    # Sentence 3: internal abatement cost = fixed mobilization + per-ton cost on tons abated.
    fixed_cost = grab(r"Mobilizing internal abatement costs(?: USD)? {N}", text)
    per_ton_cost = grab(r"plus(?: USD)? {N}(?: USD)? for each ton internally abated", text)
    internal_cost = fixed_cost + per_ton_cost * planned_abatement

    # Sentence 4: credits for the same planned quantity cost P * (Q / tons_per_credit).
    credits_needed = planned_abatement / tons_per_credit
    if credits_needed == 0:
        raise ValueError("planned abatement is zero; break-even price undefined")
    breakeven_price = internal_cost / credits_needed  # USD per ton CO2e

    return {
        "final": breakeven_price,
        "slots": {"planned_abatement_checkpoint": planned_abatement},
    }
