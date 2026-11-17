"""h038 -- tax-loss harvesting with a tracking-shortfall replacement exposure.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction
import re

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h038"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate; if written as 'N percent' / 'N%', convert to a ratio."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx + r"(\s*(?:percent|%))?", text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def solve(text: str, q: dict) -> dict:
    # S1: "An investor realizes a fully usable eligible loss magnitude of L USD."
    loss = grab(r"eligible loss magnitude of {N}\s*USD", text)
    loss = abs(loss)  # a "magnitude"

    # S2: "The applicable current-year tax rate is t, so the immediate tax reduction is available at time 0."
    tax_rate = _rate(r"current-year tax rate is {N}", text)
    tax_reduction = loss * tax_rate  # immediate current-year tax reduction (fully usable, no offset limits)

    # S3: "The tax-harvest path invests the original P USD principal plus that tax reduction ..."
    principal = grab(r"original {N}\s*USD principal", text)
    harvest_invested = principal + tax_reduction

    # S4: "The replacement earns an annual effective total-return rate equal to the intended rate r
    #      minus the additive annual tracking shortfall s."
    intended_rate = _rate(r"intended rate {N}", text)
    shortfall = _rate(r"tracking shortfall {N}", text)
    replacement_rate = intended_rate - shortfall

    # S5: "In the no-harvest counterfactual, the same original principal remains in the intended
    #      exposure and no tax reduction is received."
    no_harvest_invested = principal

    # S6: "Both paths compound annually for n years with dividends reinvested and no intermediate cash flow."
    years = grab(r"compound annually for {N}\s*years?", text)
    assert years.denominator == 1
    n = int(years)

    harvest_terminal = harvest_invested * (1 + replacement_rate) ** n
    no_harvest_terminal = no_harvest_invested * (1 + intended_rate) ** n

    # S7/S8: ignore wash-sale, fees, offset limits, future basis-tax consequences.
    # S9: "Compute the signed terminal wealth advantage of the tax-harvest path over the no-harvest path in USD."
    advantage = harvest_terminal - no_harvest_terminal

    return {
        "final": advantage,
        "slots": {"immediate_tax_reduction_checkpoint": tax_reduction},
    }
