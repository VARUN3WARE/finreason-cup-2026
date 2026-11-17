"""Data loading, structural signatures, and template routing."""

from __future__ import annotations

import difflib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = ROOT / "toolkit"
DEV_DIR = TOOLKIT / "public/task1/data/development"
TEST_DIR = TOOLKIT / "public/task1/data/test"
WORK = ROOT / "work"

SPLIT_FILES = {
    "train": DEV_DIR / "train_questions.jsonl",
    "dev": DEV_DIR / "dev_questions.jsonl",
    "lb": DEV_DIR / "leaderboard_questions.jsonl",
    "test": TEST_DIR / "test_questions.jsonl",
}
GOLD_FILES = {"train": DEV_DIR / "train_gold.jsonl", "dev": DEV_DIR / "dev_gold.jsonl"}
MANIFEST_FILES = {"train": DEV_DIR / "train_manifest.jsonl", "dev": DEV_DIR / "dev_manifest.jsonl"}

ANSWER_FORMAT_MARKER = "\n\nAnswer format:"
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:/\d+)?")


def _jsonl(path: Path) -> list[dict]:
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


@lru_cache(maxsize=None)
def questions(split: str) -> tuple[dict, ...]:
    return tuple(_jsonl(SPLIT_FILES[split]))


@lru_cache(maxsize=None)
def gold(split: str) -> dict[str, dict]:
    return {row["case_id"]: row for row in _jsonl(GOLD_FILES[split])}


@lru_cache(maxsize=None)
def manifest(split: str) -> dict[str, dict]:
    return {row["case_id"]: row for row in _jsonl(MANIFEST_FILES[split])}


def body(question: dict) -> str:
    """Question text without the generic answer-format suffix."""
    return question["question"].split(ANSWER_FORMAT_MARKER)[0]


def answer_format(question: dict) -> str:
    text = question["question"]
    idx = text.find(ANSWER_FORMAT_MARKER)
    return "" if idx < 0 else text[idx + 2 :]


def skeleton(question: dict) -> str:
    return NUM_RE.sub("#", body(question))


def signature(question: dict) -> str:
    """Answer spec + ordered slot ids/descriptions/specs: identical within a template."""
    return json.dumps(
        {
            "answer_spec": question["answer_spec"],
            "slots": [
                (s["slot_id"], s["description"], s["result_spec"])
                for s in question["trace_spec"]["slots"]
            ],
        },
        sort_keys=True,
    )


@lru_cache(maxsize=None)
def _seen_index() -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    sig_to_templates: dict[str, set[str]] = {}
    template_skeletons: dict[str, list[str]] = {}
    for split in ("train", "dev"):
        man = manifest(split)
        for q in questions(split):
            tid = man[q["case_id"]]["template_id"]
            sig_to_templates.setdefault(signature(q), set()).add(tid)
            template_skeletons.setdefault(tid, []).append(skeleton(q))
    return sig_to_templates, template_skeletons


def labeled_template(case_id: str) -> str | None:
    for split in ("train", "dev"):
        row = manifest(split).get(case_id)
        if row:
            return row["template_id"]
    return None


def route(question: dict) -> tuple[str | None, float]:
    """Return (seen template id or None, skeleton similarity of the match)."""
    known = labeled_template(question["case_id"])
    if known:
        return known, 1.0
    sig_to_templates, template_skeletons = _seen_index()
    candidates = sig_to_templates.get(signature(question))
    if not candidates:
        return None, 0.0
    sk = skeleton(question)
    best, best_score = None, -1.0
    for tid in sorted(candidates):
        score = max(
            difflib.SequenceMatcher(None, sk, other, autojunk=False).ratio()
            for other in template_skeletons[tid]
        )
        if score > best_score:
            best, best_score = tid, score
    return best, best_score


@lru_cache(maxsize=None)
def template_members() -> dict[str, dict[str, list[str]]]:
    """template_id -> split -> case ids (lb/test assigned by routing; cached on disk)."""
    cache = WORK / "template_members.json"
    if cache.exists():
        return json.loads(cache.read_text())
    members: dict[str, dict[str, list[str]]] = {}
    for split in ("train", "dev", "lb", "test"):
        for q in questions(split):
            tid, _ = route(q)
            if tid is None:
                continue
            members.setdefault(tid, {}).setdefault(split, []).append(q["case_id"])
    WORK.mkdir(exist_ok=True)
    cache.write_text(json.dumps(members, indent=1, sort_keys=True))
    return members


@lru_cache(maxsize=None)
def by_id() -> dict[str, dict]:
    out = {}
    for split in SPLIT_FILES:
        for q in questions(split):
            out[q["case_id"]] = q
    return out


def template_slug(template_id: str) -> str:
    """fp.domain.topic.name.difficulty.v1 -> module-safe slug."""
    parts = template_id.split(".")
    if parts and parts[0] == "fp":
        parts = parts[1:]
    return "__".join(parts)
