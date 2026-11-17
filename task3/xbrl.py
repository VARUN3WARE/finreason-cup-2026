"""Parsing helpers for FinReason Task 3 queries (XBRL filing snippets packed into one prompt)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

SECTIONS = ["##Schema document", "##Presentation linkbase document", "##Calculation linkbase document",
            "##Definition linkbase document", "##Label linkbase document", "##Instance document",
            "##US GAAP Taxonomy"]
QUESTION = re.compile(r"Question1:.*?reported value of\s+([\w.-]+:[\w.-]+).*?period\s+(\d{4}-\d{2}-\d{2})"
                      r"(?:\s+to\s+(\d{4}-\d{2}-\d{2}))?", re.S)


def sections(query: str) -> dict[str, str]:
    out = {}
    idx = [(query.find(h), h) for h in SECTIONS if query.find(h) >= 0]
    idx.sort()
    q1 = query.find("Question1:")
    for i, (s, h) in enumerate(idx):
        e = idx[i + 1][0] if i + 1 < len(idx) else (q1 if q1 > s else len(query))
        out[h.strip("#").strip()] = query[s:e]
    return out


@dataclass
class Target:
    concept: str
    start: str
    end: str | None


def target(query: str) -> Target | None:
    m = QUESTION.search(query)
    return Target(m.group(1), m.group(2), m.group(3)) if m else None


@dataclass
class Context:
    id: str
    start: str | None
    end: str | None
    instant: str | None
    dims: tuple = ()


CONTEXT = re.compile(r"<(?:xbrli:)?context\b[^>]*\bid=\"([^\"]+)\"[^>]*>(.*?)</(?:xbrli:)?context>", re.S)


def contexts(instance: str) -> dict[str, Context]:
    out = {}
    for m in CONTEXT.finditer(instance):
        body = m.group(2)
        g = lambda t: (re.search(rf"<(?:xbrli:)?{t}>\s*([^<]+?)\s*</", body) or [None, None])[1]
        explicit = re.findall(r"<(?:xbrldi:)?explicitMember\b[^>]*dimension=\"([^\"]+)\"[^>]*>\s*([^<]+?)\s*<", body)
        typed = [(axis, "<typed>" + re.sub(r"<[^>]+>|\s+", "", inner)) for axis, inner in re.findall(
            r"<(?:xbrldi:)?typedMember\b[^>]*dimension=\"([^\"]+)\"[^>]*>(.*?)</(?:xbrldi:)?typedMember>", body, re.S)]
        dims = tuple(sorted(explicit + typed))
        out[m.group(1)] = Context(m.group(1), g("startDate"), g("endDate"), g("instant"), dims)
    return out


@dataclass
class Fact:
    concept: str
    context: str
    raw: str
    decimals: str | None
    unit: str | None
    sign_attr: str | None


FACT = re.compile(r"<([\w.-]+):([\w.-]+)(?=[\s/>])([^>]*?)(?:/>|>([^<]*)</\1:\2>)", re.S)


def attr(attrs: str, name: str) -> str | None:
    m = re.search(r"\b" + re.escape(name) + r"=\"([^\"]*)\"", attrs)
    return m.group(1) if m else None


def facts(instance: str) -> list[Fact]:
    out = []
    for m in FACT.finditer(instance):
        prefix, local, attrs, raw = m.groups()
        ctx = attr(attrs, "contextRef")
        if not ctx:
            continue
        out.append(Fact(f"{prefix}:{local}", ctx, (raw or "").strip(), attr(attrs, "decimals"),
                        attr(attrs, "unitRef"), attr(attrs, "sign")))
    return out


def num(text: str | None) -> Decimal | None:
    if text is None:
        return None
    t = str(text).strip().replace(",", "").replace("$", "")
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()")
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    if not v.is_finite():
        return None
    return -v if neg else v


CALC_ARC = re.compile(r"<(?:link:)?calculationArc\b([^>]*)/?>")
CALC_LINK = re.compile(r"<(?:link:)?calculationLink\b([^>]*)>(.*?)</(?:link:)?calculationLink>", re.S)
LOC = re.compile(r"<(?:link:)?loc\b([^>]*)/?>")


def calc_arcs(calc: str) -> list[tuple[str, str, Decimal, str]]:
    """(parent, child, weight, role) using loc labels -> hrefs to resolve concepts."""
    out = []
    links = CALC_LINK.findall(calc) or [("", calc)]
    for link_attrs, body in links:
        role = attr(link_attrs, "xlink:role") or ""
        labels = {}
        for m in LOC.finditer(body):
            a = m.group(1)
            lab, href = attr(a, "xlink:label"), attr(a, "xlink:href")
            if lab and href and "#" in href:
                frag = href.split("#", 1)[1]
                if "_" in frag:
                    p, _, l = frag.partition("_")
                    labels[lab] = f"{p}:{l}"
        for m in CALC_ARC.finditer(body):
            a = m.group(1)
            frm, to, w = attr(a, "xlink:from"), attr(a, "xlink:to"), attr(a, "weight")
            if frm in labels and to in labels and w is not None:
                out.append((labels[frm], labels[to], Decimal(w), role))
    return out
