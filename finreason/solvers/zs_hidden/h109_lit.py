"""h109 -- minimum inventory sale (partly retained, partly repaying liabilities) to hit a target quick ratio.

Literal transcription, sentence by sentence:

S1 "A company has {Q} USD of quick assets excluding inventory and {L} USD of current liabilities."
S2 "Its required post-transaction quick ratio is one plus positive uplift ratio {u}."
       -> target ratio R = 1 + u
S3 "It can sell sufficient inventory at net recovery rate {r} of carrying amount."
       -> recovered cash = r * S   (S = inventory carrying amount sold; no cap on S)
S4 "Fraction {f} of the recovered cash remains in quick assets, while the complementary
    fraction immediately repays current liabilities at par."
       -> retained cash = f * r * S ; repayment = (1 - f) * r * S
S5 "The recovery rate is net of all modeled sale costs, and there are no other balance changes."
       -> post quick assets = Q + f r S ; post current liabilities = L - (1 - f) r S
S6 "What minimum inventory carrying amount must be sold to reach the required quick ratio exactly?"
       -> (Q + f r S) / (L - (1 - f) r S) = R, which is linear in S:
          Q + f r S = R L - R (1 - f) r S
          r S (f + R (1 - f)) = R L - Q
          S = (R L - Q) / (r (f + R (1 - f)))
       The post-sale quick ratio is strictly increasing in S (numerator rises, denominator falls),
       so this root is the unique, hence minimum, amount that reaches the target exactly.

Checkpoint (position 1) "target-weighted liability-repayment contribution" (ratio):
       per unit of recovered cash, retained cash contributes f to the target condition and the
       liability-repayment fraction (1 - f) contributes (1 - f) weighted by the target ratio R
       (each dollar of liabilities repaid lowers the required quick assets R * liabilities by R):
          liability_relief_weight = R * (1 - f)
All values are returned unrounded; the framework applies the 6-dp / 2-dp half-up rounding, so the
displayed checkpoint is never fed into the final calculation.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h109"


def solve(text: str, q: dict) -> dict:
    # S1
    quick_assets = grab(r"has {N} USD of quick assets excluding inventory", text)
    current_liabilities = grab(r"and {N} USD of current liabilities", text)
    # S2
    uplift = grab(r"one plus positive uplift ratio {N}", text)
    target_ratio = Fraction(1) + uplift
    # S3
    recovery_rate = grab(r"net recovery rate {N} of carrying amount", text)
    # S4
    retained_fraction = grab(r"Fraction {N} of the recovered cash remains in quick assets", text)
    repay_fraction = Fraction(1) - retained_fraction  # "the complementary fraction"

    # Checkpoint: target-weighted liability-repayment contribution (per unit of recovered cash)
    liability_relief_weight = target_ratio * repay_fraction

    # S5/S6: solve (Q + f r S) / (L - (1-f) r S) = R for S
    gap = target_ratio * current_liabilities - quick_assets
    cash_effectiveness = retained_fraction + liability_relief_weight  # f + R(1-f)
    required_cash = gap / cash_effectiveness
    inventory_sold = required_cash / recovery_rate

    # exactness / feasibility checks on the transcribed balances
    recovered_cash = recovery_rate * inventory_sold
    post_quick = quick_assets + retained_fraction * recovered_cash
    post_liabilities = current_liabilities - repay_fraction * recovered_cash
    assert post_liabilities > 0, "liabilities fully repaid before reaching the target"
    assert post_quick / post_liabilities == target_ratio

    return {
        "final": inventory_sold,
        "slots": {"liability_relief_weight_checkpoint": liability_relief_weight},
    }
