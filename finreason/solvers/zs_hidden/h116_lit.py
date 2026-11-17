"""h116 -- maximum COGS that exactly meets a required operating margin (literal transcription).

Text (one sentence of data + one sentence of reporting):
  "Given projected revenue of R, operating expenses of X, and a required operating margin of M,
   determine the maximum COGS that can be incurred while exactly meeting the margin requirement.
   Report the result in USD millions."

Definitions used (standard income-statement identities, nothing else is stated):
  operating income  = revenue - COGS - operating expenses
  operating margin  = operating income / revenue
  "exactly meeting" the requirement: operating margin == required margin (as a ratio)
  => COGS_max = revenue - operating expenses - required_margin_ratio * revenue
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h116"

_MONEY = r"(?:USD\s*|\$\s*)?"


def solve(text: str, q: dict) -> dict:
    # Sentence 1, clause 1: "Given projected revenue of R"
    revenue = grab(r"projected revenue of " + _MONEY + r"{N}", text)
    # Sentence 1, clause 2: "operating expenses of X"
    operating_expenses = grab(r"operating expenses of " + _MONEY + r"{N}", text)
    # Sentence 1, clause 3: "a required operating margin of M" -- stated in percent
    # (checkpoint 1: "Convert the required operating margin from percent to a ratio").
    required_margin_pct = grab(r"required operating margin of {N}", text)

    # Checkpoint 1: required operating margin as a ratio.
    target_margin_ratio = required_margin_pct / 100

    # Sentence 1, clause 4: "determine the maximum COGS that can be incurred while exactly
    # meeting the margin requirement":
    #   (revenue - COGS - operating_expenses) / revenue = target_margin_ratio
    required_operating_income = target_margin_ratio * revenue
    max_cogs = revenue - operating_expenses - required_operating_income

    # Sentence 2: "Report the result in USD millions." -- inputs are already in USD millions.
    return {
        "final": Fraction(max_cogs),
        "slots": {"target_margin_ratio_checkpoint": Fraction(target_margin_ratio)},
    }
