"""Document validity matrix: document -> category; category accepted for the requested purpose?"""
import re

TEMPLATE_ID = "fp.finance_regulation.kyc.document_validity.basic.v1"


def _split(ids: str) -> list:
    return [s.strip() for s in re.split(r",\s*(?:and\s+)?|\s+and\s+", ids) if s.strip()]


def solve(text: str, q: dict) -> dict:
    doc = re.search(r"The submitted document is ([a-z_]+)", text).group(1)
    use = re.search(r"The requested use is ([a-z_]+)", text).group(1)

    cats = {}
    for ids, cat in re.findall(r"The identifiers? ([a-z_, ]+?) (?:are|is) ([a-z_]+)\.", text):
        for ident in _split(ids):
            cats[ident] = cat
    accepts = {}
    for purpose, cs in re.findall(r"[Tt]he purpose ([a-z_]+) accepts ([a-z_ ]+?)(?:;|\.)", text):
        accepts[purpose] = set(re.split(r"\s+or\s+", cs.strip()))

    category = cats[doc]
    valid = category in accepts.get(use, set())
    return {"final": "true" if valid else "false", "slots": {"document_category": category}}
