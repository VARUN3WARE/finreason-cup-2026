# FINANCE MODEL -- cluster h116: maximum COGS that still delivers a required operating margin
# ===========================================================================================
#
# Quantity being computed
#   The largest cost of goods sold (COGS) a firm can incur, given projected revenue and operating
#   expenses, such that its operating margin is EXACTLY the required margin.
#
# Standard income-statement identities (no overrides stated in the text):
#       Gross profit      = Revenue - COGS
#       Operating income  = Gross profit - Operating expenses      (OpEx excludes COGS; COGS is the
#                         = Revenue - COGS - OpEx                    unknown being solved for)
#       Operating margin  = Operating income / Revenue
#
# Inputs (all dollar amounts are USD millions; the answer is reported in USD millions as well):
#       R   = projected revenue
#       X   = operating expenses
#       p   = required operating margin, given as a PERCENT number (e.g. 36 means 36%)
#
# Derivation
#   Step 1 (checkpoint "target_margin_ratio_checkpoint", unit ratio):
#           m = p / 100                          (percent -> plain ratio; no rounding before use)
#   Step 2: required operating income = m * R
#   Step 3: the margin requirement is a floor (margin >= m). Operating income falls one-for-one as
#           COGS rises, so the maximum admissible COGS is the point where the margin is exactly m:
#               (R - COGS - X) / R = m   =>   COGS_max = R - X - m*R = R * (1 - m) - X
#
# Conventions / notes
#   * Everything is exact Fraction arithmetic; the framework applies half-up rounding at the end
#     (final: 2 dp in USD millions; checkpoint: 6 dp as a ratio). Nothing is rounded inside the chain,
#     so the checkpoint's 6 dp rounding is never fed forward ("exact arithmetic through all steps").
#   * Exact ties are possible after rounding (e.g. 21.265 -> 21.27 half up, 0.3416355 -> 0.341636);
#     returning exact Fractions makes the framework's half-up rounding decide them correctly.
#   * The margin is on REVENUE (not on costs): "operating margin" = operating income / revenue.
#   * A negative COGS_max would just be reported as computed (no floor is mentioned in the text);
#     none of the instances produces one.
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401  (exact parsing helpers)

TEMPLATE_ID = "h116"


def solve(text: str, q: dict) -> dict:
    # --- parse inputs, anchored on the surrounding words ---------------------------------------
    revenue = grab(r"projected revenue of\s+{N}", text)           # USD millions
    opex = grab(r"operating expenses of\s+{N}", text)             # USD millions
    margin_pct = grab(r"required operating margin of\s+{N}", text)  # percent number

    # --- Step 1: percent -> ratio (checkpoint) --------------------------------------------------
    margin_ratio = margin_pct / 100

    # --- Step 2/3: operating income needed, then the COGS that leaves exactly that much ---------
    required_operating_income = margin_ratio * revenue
    cogs_max = revenue - opex - required_operating_income          # = revenue * (1 - m) - opex

    # Internal invariant: plugging the answer back gives exactly the required margin.
    assert (revenue - cogs_max - opex) / revenue == margin_ratio

    return {
        "final": cogs_max,
        "slots": {"target_margin_ratio_checkpoint": margin_ratio},
    }
