"""DQC_US_0126 (FS calculation check with non-dimensional data), following the official XULE source.

Source: DataQualityCommittee/dqc_us_rules source/us/2026/DQC_0126.xule (+ constant.xule, functions.xule).
  * networks: presentation roles whose definition contains '- Statement -' (case-sensitive), minus URI/definition
    exclusion lists; roles that are the drs-role of a statement hypercube are skipped (rule 118 covers tables);
  * calc network = the calculation link with the same role URI; one level of summation-item children;
  * fs_decimals = most frequent decimals among non-dimensional facts of the role's parent concepts (all periods);
  * total = non-dimensional target-period fact with decimals == fs_decimals;
  * addend per child = first fact with decimals == fsd, else >= fsd, else < fsd; same unit as the total;
  * fires iff |round(total, d) - round(sum, d)| > 10^-d * (children found + 1), d = fs_decimals;
  * the message reports the total and the (weighted, unrounded) sum of the children found.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from decimal import ROUND_HALF_EVEN, Decimal, localcontext

from rules import Case, fact_value
from xbrl import attr

PRES_EXCL = ["parenthetical", "equity", "deficit", "stockholders", "capital", "investment", "change", "shareholder",
             "convertible", "preferred", "temporaryequity", "redeemable", "netproceedsfromallsources",
             "membersinterest", "membershipinterest", "highlights", "employee", "ebp"]
DESC_EXCL = ["schedule iii", "schedule iv", "net worth"]
CUBE_EXCL = ["parenthetical", "equity", "deficit", "stockholders", "capital", "investment", "changes", "shareholder",
             "convertible", "preferred", "temporaryequity", "redeemable", "netproceedsfromallsources",
             "membersinterest"]
INF = Decimal("Infinity")


def role_definitions(case: Case) -> dict[str, str]:
    out = {}
    schema = case.s.get("Schema document", "")
    for m in re.finditer(r"<(?:link:)?roleType\b[^>]*roleURI=\"([^\"]+)\"[^>]*>(.*?)</(?:link:)?roleType>", schema, re.S):
        d = re.search(r"<(?:link:)?definition>([^<]*)</", m.group(2))
        out[m.group(1)] = d.group(1) if d else ""
    return out


def presentation_roles(case: Case) -> list[str]:
    pres = case.s.get("Presentation linkbase document", "")
    return [r for r in (attr(m.group(1), "xlink:role") for m in
                        re.finditer(r"<(?:link:)?presentationLink\b([^>]*)>", pres)) if r]


def statement_cube_roles(case: Case, defs: dict[str, str]) -> set[str]:
    d = case.s.get("Definition linkbase document", "")
    out = set()
    for m in re.finditer(r"<(?:link:)?definitionLink\b([^>]*)>(.*?)</(?:link:)?definitionLink>", d, re.S):
        role = attr(m.group(1), "xlink:role") or ""
        if "arcrole/all" not in m.group(2) and "arcrole/notAll" not in m.group(2):
            continue
        desc = defs.get(role, "")
        if "- Statement -" in desc and not any(x in role.lower() for x in CUBE_EXCL) \
                and "schedule iii" not in desc.lower() and "schedule iv" not in desc.lower():
            out.add(role)
    return out


def statement_ok(role: str, defs: dict[str, str]) -> bool:
    desc = defs.get(role, "")
    return ("- Statement -" in desc and not any(x in role.lower() for x in PRES_EXCL)
            and not any(x in desc.lower() for x in DESC_EXCL))


def decimals_of(f) -> Decimal | None:
    if f.decimals is None:
        return None
    return INF if f.decimals.upper() == "INF" else Decimal(f.decimals)


def most_frequent(values: list[Decimal]) -> Decimal:
    counts = Counter(values)
    top = max(counts.values())
    winner = None
    for v in dict.fromkeys(values):  # XULE builds {count: value}; the last value with the top count wins
        if counts[v] == top:
            winner = v
    return winner


def xround(v: Decimal, d: Decimal) -> Decimal:
    if d == INF:
        return v
    with localcontext() as ctx:
        ctx.prec = 400
        q = Decimal(1).scaleb(-int(d))
        return (v / q).quantize(Decimal(1), rounding=ROUND_HALF_EVEN) * q


def evaluate(case: Case) -> list[dict]:
    """One record per presentation role in which the target is a summation parent."""
    defs = role_definitions(case)
    cubes = statement_cube_roles(case, defs)
    arcs_by_role = defaultdict(list)
    for p, c, w, role in case.arcs:
        arcs_by_role[role].append((p, c, w))
    target = case.t.concept
    out = []
    for role in sorted(set(presentation_roles(case))):
        arcs = arcs_by_role.get(role, [])
        parents = list(dict.fromkeys(p for p, _, _ in arcs))
        if target not in parents:
            continue
        rec = {"role": role, "statement": statement_ok(role, defs), "cube": role in cubes}
        decs = [decimals_of(f) for f in case.facts
                if f.concept in parents and f.context in case.ctxs and not case.ctxs[f.context].dims and f.raw]
        decs = [d for d in decs if d is not None]
        if not decs:
            continue
        fsd = most_frequent(decs)
        totals_any = [f for f in case.period_facts(target, dims=False) if fact_value(f) is not None]
        totals = [f for f in totals_any if decimals_of(f) == fsd]
        total = totals[0] if totals else None
        unit = (total or (totals_any[0] if totals_any else None))
        unit = unit.unit if unit is not None else None
        s, n = Decimal(0), 0
        for p, c, w in arcs:
            if p != target:
                continue
            cf = [f for f in case.period_facts(c, dims=False)
                  if fact_value(f) is not None and (unit is None or f.unit == unit)]
            chosen = ([f for f in cf if decimals_of(f) == fsd]
                      or [f for f in cf if decimals_of(f) is not None and decimals_of(f) >= fsd]
                      or [f for f in cf if decimals_of(f) is not None and decimals_of(f) < fsd])
            if chosen:
                s += fact_value(chosen[0]) * w
                n += 1
        rec.update(fsd=fsd, total=total, total_value=fact_value(total) if total else None,
                   addend=s if n else None, found=n)
        fires = False
        if total is not None and n:
            tol = Decimal(0) if fsd == INF else Decimal(1).scaleb(-int(fsd)) * (n + 1)
            fires = abs(xround(rec["total_value"], fsd) - xround(s, fsd)) > tol
        rec["fires"] = fires and rec["statement"] and not rec["cube"]
        out.append(rec)
    return out


def fire(case: Case):
    """(extracted_raw, calculated_value) when DQC_0126 fires for the target, else None."""
    for rec in evaluate(case):
        if rec["fires"]:
            raw = rec["total"].raw if rec["total"].sign_attr != "-" else "-" + rec["total"].raw
            return raw, rec["addend"]
    return None
