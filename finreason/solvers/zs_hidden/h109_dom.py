"""h109 -- minimum inventory carrying amount to sell to hit a required post-transaction quick ratio.

FINANCE MODEL (written before the code)
=======================================
Quantities (all USD unless stated)
    Q    quick assets *excluding inventory*   (cash + receivables + securities; inventory is NOT a quick asset,
                                               so removing inventory from the books does not touch Q)
    L    current liabilities
    u    "positive uplift ratio"
    R    required post-transaction quick ratio = 1 + u      (the text says "one plus ... uplift ratio": R is
                                                             an absolute ratio such as 1.25, NOT a relative bump
                                                             on the current ratio)
    rho  net recovery rate: cash actually received per 1 USD of inventory carrying amount.
         The text says it is already net of every modeled sale cost and that there are no other balance changes,
         so no extra fee / tax / write-down step exists.
    phi  fraction of the recovered cash that stays on the balance sheet as a quick asset
    1-phi  complementary fraction of the recovered cash, paid straight to current liabilities at par
           (1 USD of cash retires exactly 1 USD of liability; that cash never sits in quick assets afterwards)
    x    UNKNOWN inventory carrying amount sold

Transaction mechanics (sell inventory of carrying amount x)
    recovered cash          c = rho * x
    quick assets after      Q' = Q + phi * c          (inventory leaves the non-quick bucket, cash enters the quick one)
    current liabilities after L' = L - (1 - phi) * c   (repayment at par)
    quick ratio after       Q' / L'   is strictly increasing in x while L' > 0, so "the minimum x that reaches the
                                       required ratio exactly" is the unique root of  Q' / L' = R.

Closed form (linear in c)
    Q + phi*c = R * (L - (1-phi)*c)
    Q + phi*c + R*(1-phi)*c = R*L
    c * [ phi + R*(1-phi) ] = R*L - Q
    c = (R*L - Q) / (phi + w),          where   w = R * (1 - phi)
    x = c / rho                                   (gross the net cash back up to carrying amount)

    Reading of the equation: one recovered dollar does two jobs.  The retained share phi adds phi to the
    numerator (quick assets).  The repaid share (1-phi) removes (1-phi) from the denominator, and because the target
    ratio R multiplies the denominator, each dollar of liability relief lowers the quick-asset requirement by R.
    So the repaid share enters the balance equation with weight R*(1-phi): this is the "target-weighted
    liability-repayment contribution" = "liability relief weight" = w.

CHECKPOINT (slot liability_relief_weight_checkpoint, unit ratio, 6 dp half-up)
    w = R * (1 - phi) = (1 + u) * (1 - phi)       -- per 1 USD of RECOVERED CASH.
    Judgement call: the recovery rate rho is a separate cash -> carrying-amount conversion that only appears in
    the last step (x = c / rho), so it is NOT folded into the weight.  (The alternative per-carrying-USD scaling
    would be rho * w; rejected because the description mentions only "target-weighted liability-repayment".)

FINAL ANSWER (unit usd, 2 dp half-up applied by the framework)
    x = (R*L - Q) / ( rho * (phi + R*(1-phi)) )   -- returned unrounded (exact Fraction).
    The framework rounds; nothing displayed is fed back into the calculation.

Sanity checks done by hand: Q/L < R in every instance (so x > 0), and L' = L - (1-phi)*rho*x > 0 (so the
ratio is well defined), and re-computing Q'/L' with the returned x reproduces R exactly (see _verify).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h109"

SLOT_WEIGHT = "liability_relief_weight_checkpoint"


def _verify(q_assets, liabilities, required, rho, phi, x):
    """Exact re-derivation of the post-transaction quick ratio from x (development self-check)."""
    cash = rho * x
    qa_after = q_assets + phi * cash
    cl_after = liabilities - (1 - phi) * cash
    return cl_after != 0 and qa_after / cl_after == required


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on surrounding words; exact Fractions) -------------------------------------------
    quick = grab(r"has {N} USD of quick assets excluding inventory", text)          # Q
    liab = grab(r"{N} USD of current liabilities", text)                            # L
    uplift = grab(r"one plus positive uplift ratio {N}", text)                      # u
    rho = grab(r"net recovery rate {N} of carrying amount", text)                   # rho
    phi = grab(r"Fraction {N} of the recovered cash remains in quick assets", text)  # phi

    # --- model ---------------------------------------------------------------------------------------------
    required = 1 + uplift                       # R: required post-transaction quick ratio
    repaid_share = 1 - phi                      # complementary fraction repaying current liabilities at par
    relief_weight = required * repaid_share     # w = R * (1 - phi)  (checkpoint)
    net_cash_weight = phi + relief_weight       # phi + R*(1-phi): effect of 1 recovered USD on the balance equation
    cash_needed = (required * liab - quick) / net_cash_weight   # recovered cash c that hits the ratio exactly
    inventory = cash_needed / rho               # carrying amount x = c / rho

    assert isinstance(inventory, Fraction)
    assert _verify(quick, liab, required, rho, phi, inventory)

    return {"final": inventory, "slots": {SLOT_WEIGHT: relief_weight}}
