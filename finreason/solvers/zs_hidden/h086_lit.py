"""h086 -- expansion / defensive / wait decision after a revenue downturn (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h086"


def solve(text: str, q: dict) -> dict:
    # "A company starts with revenue R, faces downturn ratio d, and forecasts recovery
    #  ratio g if it makes one-period cash outlay K."
    revenue = grab(r"starts with revenue\s+{N}", text)
    downturn = grab(r"downturn ratio\s+{N}", text)
    recovery = grab(r"recovery ratio\s+{N}", text)
    outlay = grab(r"cash outlay\s+{N}", text)

    # "Baseline operating cost C rises by cost-inflation ratio i."
    base_cost = grab(r"Baseline operating cost\s+{N}", text)
    inflation = grab(r"cost-inflation ratio\s+{N}", text)
    inflated_cost = base_cost * (1 + inflation)

    # "The company has available cash X and requires one-period scenario surplus of at least S."
    cash = grab(r"available cash\s+{N}", text)
    required = grab(r"surplus of at least\s+{N}", text)

    # Downturn applied to starting revenue.
    post_downturn = revenue * (1 - downturn)

    # "Expansion surplus applies both downturn and recovery, then subtracts inflated
    #  operating cost and the cash outlay."
    expansion_revenue = post_downturn * (1 + recovery)
    expansion_surplus = expansion_revenue - inflated_cost - outlay

    # "Defensive surplus applies only the downturn and subtracts inflated operating cost."
    defensive_surplus = post_downturn - inflated_cost

    # Threshold is "at least" -> >=; cash requirement: available cash covers the outlay.
    expansion_threshold = expansion_surplus >= required
    cash_ok = cash >= outlay
    defensive_threshold = defensive_surplus >= required

    if expansion_threshold and cash_ok:
        final = "expansion"
    elif defensive_threshold:
        final = "defensive"
    else:
        final = "wait"

    return {
        "final": final,
        "slots": {"post_downturn_checkpoint": Fraction(post_downturn)},
    }
