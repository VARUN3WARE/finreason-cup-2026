"""h111 -- two-method (revenue / EBITDA multiple) valuation with a dispersion-tolerance
reconciliation policy, then EV -> equity bridge (deduct debt, add cash).

Literal transcription, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h111"


def solve(text: str, q: dict) -> dict:
    # S1: "Value a target using two methods under the buyer's stated reconciliation policy."

    # S2: "The revenue method uses revenue R and revenue multiple m_R."
    revenue = grab(r"revenue method uses revenue {N}", text)
    revenue_multiple = grab(r"revenue multiple {N}", text)
    ev_revenue = revenue * revenue_multiple  # enterprise value under the revenue method

    # S3: "The EBITDA method uses EBITDA E and EBITDA multiple m_E."
    ebitda = grab(r"EBITDA method uses EBITDA {N}", text)
    ebitda_multiple = grab(r"EBITDA multiple {N}", text)
    ev_ebitda = ebitda * ebitda_multiple  # enterprise value under the EBITDA method

    # S4: "Compare the two enterprise values: their dispersion is the higher value minus the
    #      lower value, and the permitted dispersion equals the lower value multiplied by k."
    higher_value = max(ev_revenue, ev_ebitda)
    lower_value = min(ev_revenue, ev_ebitda)
    dispersion = higher_value - lower_value
    tolerance_factor = grab(r"lower value multiplied by {N}", text)  # plain ratio (e.g. 0.2)
    permitted_dispersion = lower_value * tolerance_factor

    # S5: "If the methods are consistent within that tolerance, use their mean enterprise value;
    #      otherwise use the lower enterprise value."
    #     "within that tolerance" read inclusively: dispersion <= permitted dispersion.
    consistent = dispersion <= permitted_dispersion
    if consistent:
        reconciled_ev = (ev_revenue + ev_ebitda) / 2
    else:
        reconciled_ev = lower_value

    # S6: "Then deduct total debt D and add cash C, which are the only
    #      enterprise-value-to-equity-value adjustments in this scenario."
    total_debt = grab(r"deduct total debt {N}", text)
    cash = grab(r"add cash {N}", text)
    equity_value = reconciled_ev - total_debt + cash

    # S7: "Report the reconciled equity value."
    return {
        "final": Fraction(equity_value),
        "slots": {
            "revenue_value_checkpoint": Fraction(ev_revenue),
            "ebitda_value_checkpoint": Fraction(ev_ebitda),
        },
    }
