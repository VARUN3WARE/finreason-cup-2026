"""h090: three-stage leverage-covenant ratchet; pick financing package with lower L/A ratio."""
import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h090"


def solve(text: str, q: dict) -> dict:
    assets0 = grab(r"begins with assets of {N}", text)
    liab0 = grab(r"assets of [^ ]+ and liabilities of {N}", text)
    ea, da = (grab(r"Package A adds equity proceeds of {N}", text),
              grab(r"Package A adds equity proceeds of [^ ]+ and debt proceeds of {N}", text))
    eb, db = (grab(r"Package B adds equity proceeds of {N}", text),
              grab(r"Package B adds equity proceeds of [^ ]+ and debt proceeds of {N}", text))
    start = grab(r"ceiling starts at {N}", text)
    t = grab(r"by the same fraction {N}", text)
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    m = re.search(r"internal (\w+)-stage", text)
    stages = 3
    if m:
        w = m.group(1).lower()
        stages = words.get(w, int(w) if w.isdigit() else 3)
    min_equity = grab(r"post-financing equity is at least {N}", text)

    # One-stage cap factor: the multiplier applied to the remaining ceiling each stage.
    factor = 1 - t
    ceiling = start * factor ** stages

    equity0 = assets0 - liab0
    results = {}
    for name, e, d in (("Package A", ea, da), ("Package B", eb, db)):
        equity = equity0 + e
        liab = liab0 + d
        assets = assets0 + e + d
        ratio = Fraction(liab) / assets
        qualifies = equity >= min_equity and ratio <= ceiling
        results[name] = (qualifies, ratio)

    qa, ra = results["Package A"]
    qb, rb = results["Package B"]
    if qa and qb:
        final = "Package A" if ra <= rb else "Package B"
    elif qa:
        final = "Package A"
    elif qb:
        final = "Package B"
    else:
        final = "Neither package"

    return {"final": final, "slots": {"one_stage_leverage_cap_checkpoint": factor}}
