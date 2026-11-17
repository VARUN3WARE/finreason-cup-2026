"""DQC_US_0117 (financial statement tables dimensional cross check), following the official XULE source.

Source: DataQualityCommittee/dqc_us_rules source/us/2026/DQC_0117.xule (assertions US.0117.9574 and US.0117.10093)
and constant.xule (STATEMENT_CUBES).
  9574  per statement cube and listed axis: the non-dimensional total vs the sum of single-dimension member facts,
        summing the highest reported level of nested members (a member is skipped when an ancestor has a fact);
        SubTotalExists gate; tolerance 2*10^-t with t = min(member decimals, total decimals), capped at 5.
  10093 per member SM of the axis: the single-dimension fact (axis=SM) vs the sum of all two-dimension facts
        (axis=SM, second axis = any member); used only when no 9574 message exists.
The message reports {TotalDefault} (gold extracted) and the dimensional breakdown sum (gold calculated). The dataset
treats a missing default as 0.
"""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import ROUND_HALF_EVEN, Decimal

from dqc0126 import role_definitions
from rules import AXES_0117, DEF_ARC, DEF_LINK, Case, _loc_concept, fact_value
from xbrl import attr

CUBE_EXCL = ["parenthetical", "equity", "deficit", "stockholders", "capital", "investment", "changes", "shareholder",
             "convertible", "preferred", "temporaryequity", "redeemable", "netproceedsfromallsources",
             "membersinterest"]
MISSING_DEFAULT_PREFER_10093 = True  # no reported default -> the engine leaves TotalDefault unbound; 9574 cannot fire (dev probes agree)


def parse_cubes(case: Case):
    """role -> cube {prim, axes, mem, dom, parent, unusable}; plus global dimension-default map."""
    d = case.s.get("Definition linkbase document", "")
    roles, defaults = {}, {}
    for link_attrs, body in DEF_LINK.findall(d):
        role = attr(link_attrs, "xlink:role") or ""
        locs = {}
        for m in re.finditer(r"<(?:link:)?loc\b([^>]*)/?>", body):
            a = m.group(1)
            lab, href = attr(a, "xlink:label"), attr(a, "xlink:href") or ""
            if lab:
                locs[lab] = _loc_concept(href.split("#", 1)[1] if "#" in href else lab)
        r = roles.setdefault(role, {"all": [], "hd": defaultdict(list), "dd": {}, "dm": defaultdict(list),
                                    "unusable": set()})
        for m in DEF_ARC.finditer(body):
            a = m.group(1)
            arcrole = (attr(a, "xlink:arcrole") or "").split("/")[-1]
            frm = locs.get(attr(a, "xlink:from"), _loc_concept(attr(a, "xlink:from") or ""))
            to = locs.get(attr(a, "xlink:to"), _loc_concept(attr(a, "xlink:to") or ""))
            if arcrole == "all":
                r["all"].append((frm, to))
            elif arcrole == "hypercube-dimension":
                r["hd"][frm].append(to)
            elif arcrole == "dimension-domain":
                r["dd"][frm] = to
            elif arcrole == "domain-member":
                r["dm"][frm].append(to)
                if attr(a, "xbrldt:usable") == "false":
                    r["unusable"].add(to)
            elif arcrole == "dimension-default":
                defaults[frm] = to

    def descendants(r, x):
        out, stack, seen = [], [x], set()
        while stack:
            y = stack.pop()
            for z in r["dm"].get(y, []):
                if z not in seen:
                    seen.add(z)
                    out.append(z)
                    stack.append(z)
        return out

    cubes = {}
    for role, r in roles.items():
        if not r["all"]:
            continue
        prim, axes = set(), []
        for line_items, hypercube in r["all"]:
            prim.add(line_items)
            prim |= set(descendants(r, line_items))
            axes += r["hd"].get(hypercube, [])
        mem, dom, parent = {}, {}, {}
        for ax in axes:
            dm = r["dd"].get(ax)
            dom[ax] = dm
            mem[ax] = set([dm] + descendants(r, dm)) if dm else set()
            stack = [dm] if dm else []
            while stack:
                y = stack.pop()
                for z in r["dm"].get(y, []):
                    if (ax, z) not in parent:
                        parent[(ax, z)] = y
                        stack.append(z)
        if mem:
            prim -= set().union(*mem.values())
        cubes[role] = {"prim": prim, "axes": axes, "mem": mem, "dom": dom, "parent": parent,
                       "unusable": r["unusable"]}
    return cubes, defaults


def in_cube(cube, defaults, concept, dims) -> bool:
    if concept not in cube["prim"]:
        return False
    dd = dict(dims)
    if any(a not in cube["axes"] for a in dd):
        return False
    for ax in cube["axes"]:
        if ax in dd:
            if dd[ax] not in cube["mem"][ax] or dd[ax] in cube["unusable"]:
                return False
        else:
            df = defaults.get(ax)
            if df is None or df not in cube["mem"][ax]:
                return False
    return True


def _round(v: Decimal, t: int) -> Decimal:
    q = Decimal(10) ** (-t)
    return (v / q).quantize(Decimal(1), rounding=ROUND_HALF_EVEN) * q


def tol_fires(left: Decimal, right: Decimal, decs: list[int]) -> bool:
    t = min(decs) if decs else 5
    t = 5 if t > 5 else t
    return abs(_round(left, t) - _round(right, t)) > Decimal(10) ** (-t) * 2


def _decimals(f) -> int:
    return 99 if f.decimals in (None, "INF") else int(f.decimals)


def target_facts(case: Case):
    """Target concept, question period: (dims, value, decimals, raw), de-duplicated on (dims, value, unit)."""
    out, seen = [], set()
    for f in case.period_facts(case.t.concept, dims=None):
        v = fact_value(f)
        if v is None:
            continue
        dims = case.ctxs[f.context].dims
        key = (dims, v, f.unit)
        if key in seen:
            continue
        seen.add(key)
        raw = f.raw if f.sign_attr != "-" else "-" + f.raw
        out.append((dims, v, _decimals(f), raw))
    return out


def evaluate(case: Case, statement_only: bool = True) -> list[tuple]:
    """Firing messages: ('9574'|'10093', role, axis, sub_member, total_value, total_raw, sum, n_members)."""
    cubes, defaults = parse_cubes(case)
    titles = role_definitions(case)
    concept = case.t.concept

    def is_statement(role):
        return "- statement -" in titles.get(role, "").lower() and not any(x in role.lower() for x in CUBE_EXCL)

    def is_notes(role):
        return "- disclosure -" in titles.get(role, "").lower()

    def is_paren(role):
        return "- statement -" in titles.get(role, "").lower() and "parenthetical" in role.lower()

    facts = target_facts(case)
    notes_all = [r for r in cubes if is_notes(r)]
    parens_all = [r for r in cubes if is_paren(r)]
    out = []
    for role in (r for r in cubes if (is_statement(r) or not statement_only)):
        cube = cubes[role]
        notes = [r for r in notes_all if r != role]
        parens = [r for r in parens_all if r != role]
        inc = [x for x in facts if in_cube(cube, defaults, concept, x[0])]
        for ax in cube["axes"]:
            if ax.split(":")[-1] not in AXES_0117:
                continue
            domain = cube["dom"][ax]
            # ---------------- 9574
            multi = [x for x in inc if ax in dict(x[0]) and len(x[0]) > 1]
            single = {x[0][0][1]: x for x in inc if len(x[0]) == 1 and x[0][0][0] == ax}
            subtotals_ok = all(dict(x[0])[ax] in single for x in multi)
            paren_f = [x for x in facts if len(x[0]) == 1 and x[0][0][0] == ax
                       and any(in_cube(cubes[r], defaults, concept, x[0]) for r in parens)]
            notes_f = [x for x in facts if len(x[0]) == 1 and x[0][0][0] == ax
                       and any(in_cube(cubes[r], defaults, concept, x[0]) for r in notes)]
            totals = [x for x in inc if len(x[0]) == 0]
            total = totals[0] if totals else None
            tv = total[1] if total else Decimal(0)
            notes_ok = (not notes_f) or (max(x[1] for x in notes_f) > tv)
            if subtotals_ok and notes_ok and not paren_f:
                summed = []
                for m in cube["mem"][ax] - {domain}:
                    ancestors, y = set(), m
                    while (ax, y) in cube["parent"]:
                        y = cube["parent"][(ax, y)]
                        if y != domain:
                            ancestors.add(y)
                    if any(a in single for a in ancestors):
                        continue
                    if m in single:
                        summed.append(single[m])
                if summed:
                    s = sum(x[1] for x in summed)
                    decs = [x[2] for x in summed] + ([total[2]] if total else [])
                    if tol_fires(s, tv, decs):
                        out.append(("9574", role, ax, None, tv, total[3] if total else "0", s, len(summed)))
            # ---------------- 10093
            two = [x for x in inc if ax in dict(x[0]) and len(x[0]) == 2]
            for sm in sorted({dict(x[0])[ax] for x in two}):
                second = sorted({a for x in two if dict(x[0])[ax] == sm for a, _ in x[0] if a != ax})
                d2 = second[0]
                if d2.split(":")[-1] == "LegalEntityAxis":
                    continue
                deeper = [x for x in inc if dict(x[0]).get(ax) == sm and d2 in dict(x[0]) and len(x[0]) > 2]
                if not all(any(dict(y[0]).get(ax) == sm and dict(y[0]).get(d2) == dict(x[0])[d2] and len(y[0]) == 2
                               for y in inc) for x in deeper):
                    continue
                sub_total = [x for x in inc if len(x[0]) == 1 and x[0][0] == (ax, sm)]
                if not sub_total:
                    continue
                st = sub_total[0]
                nf = [x for x in facts if len(x[0]) == 2 and dict(x[0]).get(ax) == sm and d2 in dict(x[0])
                      and any(in_cube(cubes[r], defaults, concept, x[0]) for r in notes)]
                if nf and not (max(x[1] for x in nf) > st[1]):
                    continue
                parts = [x for x in two if dict(x[0])[ax] == sm and d2 in dict(x[0])]
                s = sum(x[1] for x in parts)
                if tol_fires(s, st[1], [x[2] for x in parts] + [st[2]]):
                    out.append(("10093", role, ax, sm, st[1], st[3], s, len(parts)))
    return out


def unrestricted(case: Case):
    """Fallback: sum all single-dimension facts on a listed axis, ignoring declared members."""
    groups: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for f in case.period_facts(case.t.concept, dims=True):
        d = case.ctxs[f.context].dims
        if len(d) == 1 and d[0][0].split(":")[-1] in AXES_0117:
            v = fact_value(f)
            if v is not None:
                groups[d[0][0]].setdefault(d[0][1], v)
    return groups


def fire(case: Case, statement_only: bool = True):
    """(extracted_raw, calculated_value, mechanism) for the 0117 message the dataset most likely used, else None.

    9574 takes precedence over 10093; among several 9574 messages the axis with most summed members wins.
    """
    msgs = evaluate(case, statement_only)
    m9 = [x for x in msgs if x[0] == "9574"]
    m10 = [x for x in msgs if x[0] == "10093"]
    if MISSING_DEFAULT_PREFER_10093 and m9 and not has_default(case):
        # The open-source engine does not fire 9574 when the default (total) is not reported at all.
        m9 = []
    if m9:
        x = max(m9, key=lambda x: x[7])
        return x[5], x[6], "0117_9574" + ("" if statement_only else "_any")
    if m10:
        x = max(m10, key=lambda x: abs(x[4] - x[6]))
        return x[5], x[6], "0117_10093" + ("" if statement_only else "_any")
    return None


def statement_cube_shipped(case: Case) -> bool:
    titles = role_definitions(case)
    cubes, _ = parse_cubes(case)
    return any("- statement -" in titles.get(r, "").lower() and not any(x in r.lower() for x in CUBE_EXCL)
               for r in cubes)


def has_default(case: Case) -> bool:
    """A non-nil, numeric, non-dimensional fact for the target period (XULE 'nonils' factsets skip nil facts)."""
    return any(fact_value(f) is not None for f in case.period_facts(case.t.concept, dims=False))
