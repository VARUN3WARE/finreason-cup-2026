from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h086"


def _ratio(pattern: str, text: str) -> Fraction:
    """Grab a ratio; if it is followed by 'percent', convert to a plain ratio."""
    import re
    from finreason.nums import NUMBER
    rx = pattern.replace("{N}", f"({NUMBER})(\\s*(?:percent|%))?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def solve(text: str, q: dict) -> dict:
    revenue0 = grab(r"starts with revenue (?:of )?(?:USD )?\$?{N}", text)
    downturn = _ratio(r"downturn ratio (?:of )?{N}", text)
    recovery = _ratio(r"recovery ratio (?:of )?{N}", text)
    outlay = grab(r"cash outlay (?:of )?(?:USD )?\$?{N}", text)
    base_cost = grab(r"[Bb]aseline operating cost (?:of )?(?:USD )?\$?{N}", text)
    inflation = _ratio(r"cost-inflation ratio (?:of )?{N}", text)
    cash = grab(r"available cash (?:of )?(?:USD )?\$?{N}", text)
    threshold = grab(r"scenario surplus of at least (?:USD )?\$?{N}", text)

    post_downturn = revenue0 * (1 - downturn)
    recovered = post_downturn * (1 + recovery)
    inflated_cost = base_cost * (1 + inflation)

    expansion_surplus = recovered - inflated_cost - outlay
    defensive_surplus = post_downturn - inflated_cost

    expansion_ok = expansion_surplus >= threshold and cash >= outlay
    defensive_ok = defensive_surplus >= threshold

    if expansion_ok:
        final = "expansion"
    elif defensive_ok:
        final = "defensive"
    else:
        final = "wait"

    return {"final": final, "slots": {"post_downturn_checkpoint": post_downturn}}
