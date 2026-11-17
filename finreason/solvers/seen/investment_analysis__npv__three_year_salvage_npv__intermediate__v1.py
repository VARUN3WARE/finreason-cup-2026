from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.investment_analysis.npv.three_year_salvage_npv.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    i0 = grab(r"costs USD {N} now", text)
    cf1, cf2, cf3 = grab_all(
        r"pays USD {N}, USD {N},? and USD {N} at the ends of years one through three", text
    )
    salvage = grab(r"plus USD {N} at the end of year three", text)
    r = grab(r"discount rate {N} percent", text) / 100
    g = 1 + r
    terminal = cf3 + salvage
    pv1 = cf1 / g
    pv2 = cf2 / g**2
    pv3 = terminal / g**3
    total = pv1 + pv2 + pv3
    return {
        "final": total - i0,
        "slots": {
            "terminal_cash_flow_trace": terminal,
            "pv_three_trace": pv3,
            "total_pv_trace": total,
        },
    }
