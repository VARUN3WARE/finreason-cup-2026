"""h028 -- stylized acquisition: full-year run-rate adjusted EPS accretion/dilution.

Literal transcription, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h028"


def _frac_or_pct(pattern_frac: str, pattern_pct: str, text: str) -> Fraction:
    try:
        return grab(pattern_pct, text) / 100
    except ValueError:
        return grab(pattern_frac, text)


def solve(text: str, q: dict) -> dict:
    # S2: "The acquirer's predeal common shares have aggregate reference equity value V
    #      at one fixed contractual share price."
    predeal_equity_value = grab(r"aggregate reference equity value {N}", text)
    # The price itself is never stated; every share count is (value / price), so the price
    # cancels in every ratio.  Use an arbitrary positive price symbol.
    price = Fraction(1)
    predeal_shares = predeal_equity_value / price

    # S3: "Upfront base consideration is B, excluding the earnout; c is paid in cash and the
    #      remainder in common shares."
    base_consideration = grab(r"Upfront base consideration is {N}", text)
    cash_fraction = _frac_or_pct(r"; {N} is paid in cash", r"; {N} percent is paid in cash", text)
    upfront_cash = base_consideration * cash_fraction
    upfront_stock_value = base_consideration - upfront_cash

    # S4: "A fully realized earnout with settlement value E, incremental to the base
    #      consideration, is settled entirely in common shares at the same unchanged price,
    #      and every deal share is outstanding for the full year."
    earnout_value = grab(r"earnout with settlement value {N}", text)
    upfront_deal_shares = upfront_stock_value / price
    earnout_shares = earnout_value / price
    deal_shares = upfront_deal_shares + earnout_shares
    deal_share_ratio = deal_shares / predeal_shares          # checkpoint 1 (ratio)

    # S5: "The entire upfront cash leg is debt-funded at annual pre-tax interest rate r."
    interest_rate = _frac_or_pct(r"annual pre-tax interest rate {N}",
                                 r"annual pre-tax interest rate (?:of )?{N} percent", text)
    debt = upfront_cash
    pretax_interest = debt * interest_rate                    # checkpoint 2 (usd_million)

    # S6: "Same-period standalone after-tax net income is A for the acquirer and T for the
    #      target; target net income excludes the separately stated recurring annual pre-tax
    #      synergies of S."
    acquirer_ni = grab(r"after-tax net income is {N} for the acquirer", text)
    target_ni = grab(r"for the acquirer and {N} for the target", text)
    pretax_synergies = grab(r"annual pre-tax synergies of {N}", text)

    # S7: "With tax rate t, after-tax synergies and interest each equal their pre-tax amount
    #      times one minus that rate, and the full interest tax shield is usable."
    tax_rate = _frac_or_pct(r"With tax rate {N}", r"With tax rate (?:of )?{N} percent", text)
    aftertax_synergies = pretax_synergies * (1 - tax_rate)
    if "tax shield is usable" in text and "not usable" not in text and "unusable" not in text:
        aftertax_interest = pretax_interest * (1 - tax_rate)
    else:
        aftertax_interest = pretax_interest

    # S8: ignore everything else.
    # S9: adjusted EPS accretion/dilution vs acquirer standalone EPS, in percent.
    standalone_eps = acquirer_ni / predeal_shares
    proforma_ni = acquirer_ni + target_ni + aftertax_synergies - aftertax_interest
    proforma_shares = predeal_shares + deal_shares
    proforma_eps = proforma_ni / proforma_shares
    accretion_pct = (proforma_eps / standalone_eps - 1) * 100

    return {
        "final": accretion_pct,
        "slots": {
            "deal_share_issuance_checkpoint": deal_share_ratio,
            "pretax_interest_checkpoint": pretax_interest,
        },
    }
