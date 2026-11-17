# FINANCE MODEL (h079)
#
# Quantity: minimum reported EBITDA (USD million) that supports a target equity price.
#
# Equity-to-enterprise bridge (standard convention, no overrides in the text):
#   net debt = total debt - cash          (cash is netted against debt; may be negative = net cash)
#   EV       = target equity value + net debt
#   The text states debt and cash are the ONLY EV-to-equity adjustments, so no minorities,
#   preferred, leases, etc. enter the bridge.
#
# Valuation multiple:
#   "the buyer values normalized EBITDA at M" -> EV / normalized EBITDA = M (a plain multiple, e.g. 6x).
#   required normalized EBITDA = EV / M
#
# Quality-of-earnings adjustment:
#   "recurring EBITDA deduction of D from the reported figure" -> normalized = reported - D
#   "then restore the deduction" -> reported = normalized + D
#   minimum reported EBITDA = EV / M + D
#
# Checkpoint:
#   net_debt_checkpoint = debt - cash (position 1, usd_million, 4 dp half-up applied by framework)
#
# No rounding inside the computation; the framework rounds the final (2 dp) and checkpoint (4 dp).
# "Minimum" simply means the break-even EBITDA at which equity value equals the target.

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h079"


def solve(text: str, q: dict) -> dict:
    equity = grab(r"target equity value of {N}", text)
    debt = grab(r"total debt of {N}", text)
    cash = grab(r"cash of {N}", text)
    multiple = grab(r"normalized EBITDA at {N}", text)
    deduction = grab(r"EBITDA deduction of {N}", text)

    net_debt = debt - cash
    ev = equity + net_debt
    normalized = ev / multiple
    reported = normalized + deduction

    return {
        "final": reported,
        "slots": {"net_debt_checkpoint": net_debt},
    }
