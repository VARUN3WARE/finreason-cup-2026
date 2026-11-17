"""Re-implementations of the three DQC rules behind FinReason Task 3 cases."""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal

from xbrl import Context, Fact, Target, attr, calc_arcs, contexts, facts, num, sections, target

AXES_0117 = ["StatementClassOfStockAxis", "ProductOrServiceAxis", "PropertyPlantAndEquipmentByTypeAxis",
             "LongtermDebtTypeAxis", "RelatedPartyTransactionsByRelatedPartyAxis", "StatementBusinessSegmentsAxis",
             "FinancialInstrumentAxis", "LimitedPartnersCapitalAccountByClassAxis",
             "PartnerTypeOfPartnersCapitalAccountAxis", "FiniteLivedIntangibleAssetsByMajorClassAxis",
             "InformationByCategoryOfDebtSecurityAxis"]


def period_ok(c: Context, t: Target) -> bool:
    if t.end:
        return c.start == t.start and c.end == t.end
    return c.instant == t.start


def fact_value(f: Fact) -> Decimal | None:
    v = num(f.raw)
    if v is not None and f.sign_attr == "-":
        v = -v
    return v


class Case:
    def __init__(self, query: str):
        self.query = query
        self.s = sections(query)
        self.t = target(query)
        self.inst = self.s.get("Instance document", "")
        self.ctxs = contexts(self.inst)
        self.facts = facts(self.inst)
        self.by_concept = defaultdict(list)
        for f in self.facts:
            if f.context in self.ctxs:
                self.by_concept[f.concept].append(f)
        self.arcs = calc_arcs(self.s.get("Calculation linkbase document", ""))

    def period_facts(self, concept: str, dims: bool | None = False) -> list[Fact]:
        out = []
        for f in self.by_concept.get(concept, []):
            c = self.ctxs[f.context]
            if not period_ok(c, self.t):
                continue
            if dims is False and c.dims:
                continue
            if dims is True and not c.dims:
                continue
            out.append(f)
        return out

    def reported(self) -> tuple[str | None, Decimal | None]:
        for f in self.period_facts(self.t.concept, dims=False):
            v = fact_value(f)
            if v is not None:
                raw = f.raw if f.sign_attr != "-" else "-" + f.raw
                return raw, v
        return None, None

    # ---- DQC_0126: weighted sum of non-dimensional calculation children
    def calc_children_sum(self) -> list[tuple[str, Decimal, int, int]]:
        """Per calculation role: (role, sum, children found, children total)."""
        out = []
        roles = defaultdict(list)
        for p, c, w, role in self.arcs:
            if p == self.t.concept:
                roles[role].append((c, w))
        for role, kids in roles.items():
            total, found = Decimal(0), 0
            for c, w in kids:
                vals = [fact_value(f) for f in self.period_facts(c, dims=False)]
                vals = [v for v in vals if v is not None]
                if vals:
                    total += vals[0] * w
                    found += 1
            out.append((role, total, found, len(kids)))
        return out

    # ---- DQC_0117: sum of dimensional members on listed axes
    def member_sums(self) -> dict[str, tuple[Decimal, list]]:
        sums = {}
        groups = defaultdict(dict)
        for f in self.period_facts(self.t.concept, dims=True):
            dims = self.ctxs[f.context].dims
            if len(dims) != 1:
                continue
            axis, member = dims[0]
            if axis.split(":")[-1] not in AXES_0117:
                continue
            v = fact_value(f)
            if v is not None:
                groups[axis].setdefault(member, v)
        for axis, members in groups.items():
            sums[axis] = (sum(members.values(), Decimal(0)), sorted(members.items()))
        return sums


DEF_LINK = re.compile(r"<(?:link:)?definitionLink\b([^>]*)>(.*?)</(?:link:)?definitionLink>", re.S)
DEF_ARC = re.compile(r"<(?:link:)?definitionArc\b([^>]*)/?>")


def _loc_concept(label: str) -> str:
    """us-gaap_SegmentDomain / loc_us-gaap_X_123 -> us-gaap:SegmentDomain (best effort)."""
    body = label[4:] if label.startswith("loc_") else label
    m = re.match(r"([A-Za-z][\w.-]*?)_([A-Za-z][\w.-]*?)(?:_[0-9a-fA-F-]{6,}|_\d+)?$", body)
    if m:
        return f"{m.group(1)}:{m.group(2)}"
    p, _, rest = body.partition("_")
    return f"{p}:{rest}"


def statement_members(case: "Case") -> dict[str, set[str]]:
    """axis -> top-level members declared under that axis in statement-role hypercubes."""
    d = case.s.get("Definition linkbase document", "")
    out: dict[str, set[str]] = defaultdict(set)
    for link_attrs, body in DEF_LINK.findall(d):
        role = (attr(link_attrs, "xlink:role") or "").lower()
        if "statement" not in role and "balancesheet" not in role and "operations" not in role \
                and "cashflow" not in role and "income" not in role and "financialposition" not in role:
            pass  # role names vary; keep all roles but prefer statement roles via caller if needed
        locs = {}
        for m in re.finditer(r"<(?:link:)?loc\b([^>]*)/?>", body):
            a = m.group(1)
            lab, href = attr(a, "xlink:label"), attr(a, "xlink:href") or ""
            if lab:
                frag = href.split("#", 1)[1] if "#" in href else lab
                locs[lab] = _loc_concept(frag)
        dom_of_axis, children = {}, defaultdict(list)
        for m in DEF_ARC.finditer(body):
            a = m.group(1)
            arcrole = (attr(a, "xlink:arcrole") or "").split("/")[-1]
            frm = locs.get(attr(a, "xlink:from"), _loc_concept(attr(a, "xlink:from") or ""))
            to = locs.get(attr(a, "xlink:to"), _loc_concept(attr(a, "xlink:to") or ""))
            if arcrole == "dimension-domain":
                dom_of_axis[frm] = to
            elif arcrole == "domain-member":
                children[frm].append(to)
        for axis, dom in dom_of_axis.items():
            for mem in children.get(dom, []):
                out[axis].add(mem)
    return out


# ---------------------------------------------------------------- scope features
import json as _json
from pathlib import Path as _Path

_DQC15 = _json.loads((_Path(__file__).parent / "resources/dqc_0015.json").read_text())
ELEMENTS_0015 = set(_DQC15["elements"])


def member_excluded_0015(dims: tuple) -> bool:
    for axis, member in dims:
        a, m = axis.split(":")[-1], member.split(":")[-1]
        for ex in _DQC15["exclusions"]:
            name = str(ex["name"])
            if ex["kind"] == "Member":
                if member.startswith("<typed>"):
                    continue
                if "contains" in ex["test"] and name.lower() in m.lower():
                    return True
                if "equals" in ex["test"] and name == m:
                    return True
            elif ex["kind"] == "Axis" and name == a:
                if ex["and_member"] is None or ex["and_member"] == m:
                    return True
    return False


def required_period(case: "Case") -> tuple[str | None, str | None]:
    """(start, end) of the document's reporting period, from dei:DocumentPeriodEndDate's context."""
    for f in case.facts:
        if f.concept in ("dei:DocumentPeriodEndDate", "dei:DocumentType") and f.context in case.ctxs:
            c = case.ctxs[f.context]
            if c.start and c.end:
                return c.start, c.end
    return None, None


def is_current_period(case: "Case") -> bool | None:
    s, e = required_period(case)
    if e is None:
        return None
    t = case.t
    if t.end:
        return t.start == s and t.end == e
    return t.start == e


def calc_role_titles(case: "Case") -> dict[str, str]:
    calc = case.s.get("Calculation linkbase document", "")
    out = {}
    for m in re.finditer(r"<(?:link:)?calculationLink\b([^>]*)>", calc):
        role, title = attr(m.group(1), "xlink:role"), attr(m.group(1), "xlink:title")
        if role:
            out[role] = title or ""
    schema = case.s.get("Schema document", "")
    for m in re.finditer(r"<(?:link:)?roleType\b[^>]*roleURI=\"([^\"]+)\"[^>]*>(.*?)</(?:link:)?roleType>", schema, re.S):
        d = re.search(r"<(?:link:)?definition>([^<]*)</", m.group(2))
        if d and not out.get(m.group(1)):
            out[m.group(1)] = d.group(1)
    return out


def is_statement_role(title: str, role: str) -> bool:
    t = (title or "").lower()
    if "- statement -" in t or " statement " in f" {t} ":
        return "equity" not in t and "stockholders" not in t and "shareholders" not in t and "changes in" not in t
    r = role.lower()
    return "statement" in r and "equity" not in r


def latest_period(case: "Case") -> tuple[str | None, str | None]:
    """Infer the document period: latest end date; the longest duration ending then."""
    ends = [c.end or c.instant for c in case.ctxs.values() if (c.end or c.instant)]
    if not ends:
        return None, None
    last = max(ends)
    durs = [c for c in case.ctxs.values() if c.end == last and c.start]
    start = min((c.start for c in durs), default=None)
    return start, last


def target_is_current(case: "Case") -> bool:
    s, e = latest_period(case)
    t = case.t
    if t.end:
        return t.end == e and t.start == s
    return t.start == e


def def_roles(case: "Case") -> dict[str, dict]:
    """role -> {'axes': set, 'members': {axis: set}} for definition-linkbase roles with hypercubes."""
    d = case.s.get("Definition linkbase document", "")
    out = {}
    for link_attrs, body in DEF_LINK.findall(d):
        role = attr(link_attrs, "xlink:role") or ""
        locs = {}
        for m in re.finditer(r"<(?:link:)?loc\b([^>]*)/?>", body):
            a = m.group(1)
            lab, href = attr(a, "xlink:label"), attr(a, "xlink:href") or ""
            if lab:
                locs[lab] = _loc_concept(href.split("#", 1)[1] if "#" in href else lab)
        axes, dom_of, kids = set(), {}, defaultdict(list)
        for m in DEF_ARC.finditer(body):
            a = m.group(1)
            arcrole = (attr(a, "xlink:arcrole") or "").split("/")[-1]
            frm = locs.get(attr(a, "xlink:from"), _loc_concept(attr(a, "xlink:from") or ""))
            to = locs.get(attr(a, "xlink:to"), _loc_concept(attr(a, "xlink:to") or ""))
            if arcrole == "hypercube-dimension":
                axes.add(to)
            elif arcrole == "dimension-domain":
                dom_of[frm] = to
            elif arcrole == "domain-member":
                kids[frm].append(to)
        if axes:
            members = {ax: set(kids.get(dom_of.get(ax, ""), [])) for ax in axes}
            out[role] = {"axes": axes, "members": members, "line_items": set(sum(kids.values(), []))}
    return out
