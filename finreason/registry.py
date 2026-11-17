"""Discover solver modules: one module per template, exposing TEMPLATE_ID and solve()."""

from __future__ import annotations

import importlib
import pkgutil
from functools import lru_cache
from types import ModuleType

from .solvers import seen as seen_pkg


@lru_cache(maxsize=None)
def seen_solvers() -> dict[str, ModuleType]:
    out: dict[str, ModuleType] = {}
    for info in pkgutil.iter_modules(seen_pkg.__path__):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{seen_pkg.__name__}.{info.name}")
        tid = getattr(module, "TEMPLATE_ID", None)
        if tid is None or not callable(getattr(module, "solve", None)):
            continue
        if tid in out:
            raise RuntimeError(f"duplicate solver for {tid}: {info.name}")
        out[tid] = module
    return out


def load_one(template_id: str) -> ModuleType:
    from .data import template_slug

    name = template_slug(template_id)
    module = importlib.import_module(f"{seen_pkg.__name__}.{name}")
    importlib.reload(module)
    return module
