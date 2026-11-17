"""h061: revenue required for a target after-tax income (cost-volume-profit with tax).

NI = (Revenue * (1 - variable COGS rate) - fixed operating costs - interest) * (1 - tax rate)
=> Revenue = (NI / (1 - tax) + fixed costs + interest) / (1 - variable COGS rate)
Checkpoint: after-tax retention ratio = 1 - tax rate.
"""
import re
from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h061"


def solve(text: str, q: dict) -> dict:
    v = grab(r"variable COGS rate(?: ratio)? of {N}", text)
    fixed = grab(r"fixed operating costs of {N}", text)
    interest = grab(r"interest expense of {N}", text)
    t = grab(r"income tax rate(?: ratio)? of {N}", text)
    ni = grab(r"after-tax income of {N}", text)
    if re.search(r"variable COGS rate(?: ratio)? of [-\d.,/]+ ?(?:percent|%)", text):
        v = v / 100
    if re.search(r"income tax rate(?: ratio)? of [-\d.,/]+ ?(?:percent|%)", text):
        t = t / 100
    retention = 1 - t
    ebt = ni / retention
    revenue = (ebt + fixed + interest) / (1 - v)
    return {"final": revenue, "slots": {"retention_ratio_checkpoint": retention}}
