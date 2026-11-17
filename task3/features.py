"""Per-case rule features shared by the solver variants."""
import sys
from decimal import Decimal
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rules import (ELEMENTS_0015, Case, calc_role_titles, is_current_period, is_statement_role,  # noqa: E402
                   member_excluded_0015)
from solve import member_sums_0117  # noqa: E402


def features(query: str) -> dict:
    c = Case(query)
    raw, rep = c.reported()
    base = rep if rep is not None else Decimal(0)
    m117 = sorted([(a, t, n) for a, t, n in member_sums_0117(c) if t != base], key=lambda x: -x[2])
    sums = [x for x in c.calc_children_sum() if x[2] > 0]
    titles = calc_role_titles(c)
    c126 = None
    if sums and rep is not None:
        ro, tot, fd, n = max(sums, key=lambda x: (x[2] / x[3], x[2]))
        if tot != rep:
            c126 = {"value": tot, "stmt": is_statement_role(titles.get(ro, ""), ro), "complete": fd == n,
                    "found": fd, "n": n}
    negdims = []
    for f in c.period_facts(c.t.concept, dims=True):
        from rules import fact_value
        v = fact_value(f)
        if v is not None and v < 0 and not member_excluded_0015(c.ctxs[f.context].dims):
            negdims.append((f.raw if f.sign_attr != "-" else "-" + f.raw, v))
    return {"raw": raw, "rep": rep, "m117": m117, "c126": c126, "in15": c.t.concept in ELEMENTS_0015,
            "negdims": negdims, "current": is_current_period(c), "concept": c.t.concept}
