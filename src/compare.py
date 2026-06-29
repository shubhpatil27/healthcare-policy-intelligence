from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List
import re


@dataclass
class DiffReport:
    added: List[str]
    removed: List[str]
    modified: List[str]
    summary: str


def _sentences(text: str) -> List[str]:
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in pieces if p.strip()]


def compare_texts(old_text: str, new_text: str) -> DiffReport:
    old_lines = _sentences(old_text)
    new_lines = _sentences(new_text)
    sm = SequenceMatcher(None, old_lines, new_lines)

    added: List[str] = []
    removed: List[str] = []
    modified: List[str] = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            added.extend(new_lines[j1:j2])
        elif tag == "delete":
            removed.extend(old_lines[i1:i2])
        elif tag == "replace":
            removed.extend(old_lines[i1:i2])
            added.extend(new_lines[j1:j2])
            for a, b in zip(old_lines[i1:i2], new_lines[j1:j2]):
                modified.append(f"- {a}\n+ {b}")

    summary = (
        f"{len(added)} additions, {len(removed)} removals, and {len(modified)} direct replacements detected."
    )
    return DiffReport(added=added, removed=removed, modified=modified, summary=summary)


def format_bullets(items: List[str], empty_label: str) -> str:
    if not items:
        return empty_label
    return "\n".join(f"- {x}" for x in items[:20])
