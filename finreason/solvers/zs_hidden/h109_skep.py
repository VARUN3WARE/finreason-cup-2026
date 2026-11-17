"""h109 -- minimum inventory carrying amount to sell so that the quick ratio hits a target.

AMBIGUITY RESOLUTIONS (recorded before implementation)

A1  Quick ratio = quick assets / current liabilities.  The text's "quick assets excluding
    inventory" is the standard quick-asset base; the inventory that is sold is NOT in the
    numerator, so removing it from the balance sheet does not change quick assets.  The only
    numerator effect is the retained cash; the only denominator effect is the repayment.
A2  "required post-transaction quick ratio is one plus positive uplift ratio u" is literal:
    T = 1 + u.  Not (current ratio + u), not current ratio * (1 + u).  u is a ratio (text says
    "uplift ratio 0.25"), not a percent.
A3  "net recovery rate r of carrying amount": recovered cash = r * X where X is the carrying
    amount sold.  "net of all modeled sale costs" -> no further deduction from r * X.
A4  "Fraction a of the recovered cash remains in quick assets" -> numerator + a*r*X (cash is a
    quick asset).  "the complementary fraction immediately repays current liabilities at par"
    -> denominator - (1-a)*r*X, dollar for dollar (no premium / discount on repayment).
A5  The book loss (X - r*X) hits inventory/equity only; "no other balance changes" confirms that
    neither quick assets nor current liabilities move for any other reason.
A6  "minimum carrying amount ... to reach the required quick ratio exactly": with Q, L > 0 the
    post-transaction ratio (Q + a r X) / (L - (1-a) r X) is strictly increasing in X, so the
    minimum X is the unique root of the equality
        Q + a r X = T (L - (1-a) r X)
        X * r * (a + T (1-a)) = T L - Q
        X = (T L - Q) / (r * (a + T (1-a))).
    No floor at zero is stated in the text, so none is applied (all three instances start below
    the target, so X > 0 anyway).
A7  Checkpoint "liability_relief_weight_checkpoint" = "target-weighted liability-repayment
    contribution", unit ratio.  In the bracket (a + T (1-a)) the quick-asset retention
    contributes the plain weight a and the liability repayment contributes (1-a) weighted by the
    target T.  So the checkpoint is T * (1 - a), a dimensionless weight.  The alternative reading
    r * T * (1-a) (per unit of carrying amount) is rejected: the description names only "target"
    and "liability-repayment" and never the recovery rate, and "weight" is the blend weight whose
    quick-asset counterpart is a, not r*a.
A8  Units: the final answer is the carrying amount X in USD (not the recovered cash r*X, not the
    repayment (1-a) r X).  Both values are returned unrounded; the framework rounds (final 2 dp,
    checkpoint 6 dp, half-up).  The displayed checkpoint is never fed back into the computation.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h109"


def solve(text: str, q: dict) -> dict:
    # Opening balances (USD).
    quick = grab(r"has {N} USD of quick assets", text)
    liab = grab(r"{N} USD of current liabilities", text)

    # Target quick ratio T = 1 + uplift (A2).
    uplift = grab(r"one plus positive uplift ratio {N}", text)
    target = Fraction(1) + uplift

    # Net recovery per USD of carrying amount (A3).
    recovery = grab(r"net recovery rate {N} of carrying amount", text)

    # Fraction of recovered cash retained as quick assets; complement repays liabilities (A4).
    keep = grab(r"Fraction {N} of the recovered cash remains in quick assets", text)
    repay = Fraction(1) - keep

    # Checkpoint: target-weighted liability-repayment contribution (A7).
    liability_relief_weight = target * repay

    # Solve Q + keep*r*X = T*(L - repay*r*X) exactly for X (A6).
    numerator = target * liab - quick
    denominator = recovery * (keep + liability_relief_weight)
    carrying_amount = numerator / denominator

    return {
        "final": carrying_amount,
        "slots": {"liability_relief_weight_checkpoint": liability_relief_weight},
    }
