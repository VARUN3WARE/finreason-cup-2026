import re

TEMPLATE_ID = "fp.finance_regulation.kyc.document_validity.basic.v1"


def _split_ids(chunk: str) -> list[str]:
    return [p for p in re.split(r"\s*,\s*(?:and\s+)?|\s+and\s+|\s+or\s+", chunk.strip()) if p]


def solve(text: str, q: dict) -> dict:
    doc = re.search(r"The submitted document is (\w+)\.", text).group(1)
    use = re.search(r"The requested use is (\w+)\.", text).group(1)

    # Document -> category mapping parsed from text (permuted across instances, e.g. test rows).
    category = None
    for ids, cat in re.findall(r"The identifiers? ([\w ,]+?) (?:are|is) (\w+)\.", text):
        if doc in _split_ids(ids):
            category = cat
            break
    if category is None:
        raise ValueError(f"document {doc!r} not mapped")

    # Purpose -> accepted categories.
    accepted = {}
    for purpose, cats in re.findall(r"the purpose (\w+) accepts ([\w ,]+?)(?=[;.])", text, flags=re.I):
        accepted[purpose] = set(_split_ids(cats))
    if use not in accepted:
        raise ValueError(f"purpose {use!r} not found")

    valid = category in accepted[use]
    return {"final": "true" if valid else "false", "slots": {"document_category": category}}
