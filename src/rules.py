from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict
import json
import re


@dataclass
class Rule:
    category: str
    condition: str
    action: str
    evidence: str


def _sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def _to_condition_action(sentence: str) -> tuple[str, str]:
    lower = sentence.lower()
    if "prior authorization" in lower or "prior auth" in lower:
        return ("Policy trigger detected", sentence)
    if any(k in lower for k in ["requires", "must", "shall", "eligible", "covered", "excluded", "not covered"]):
        return ("Policy rule detected", sentence)
    return ("Informational", sentence)


def extract_rules(text: str) -> List[Rule]:
    rules: List[Rule] = []
    for sentence in _sentences(text):
        low = sentence.lower()
        if low.startswith("policy ") or low.startswith("version "):
            continue
        if not any(k in low for k in ["requires", "must", "shall", "prior authorization", "covered", "not covered", "excluded", "eligible"]):
            continue

        category = "General"
        if any(k in low for k in ["prior authorization", "prior auth", "pre-authorization", "preauthorization"]):
            category = "Prior Authorization"
        elif any(k in low for k in ["covered", "coverage", "eligible"]):
            category = "Coverage"
        elif any(k in low for k in ["not covered", "excluded", "denied", "not payable", "not reimbursable"]):
            category = "Exclusion"
        elif any(k in low for k in ["requires", "must", "shall"]):
            category = "Requirement"

        condition, action = _to_condition_action(sentence)
        rules.append(Rule(category=category, condition=condition, action=action, evidence=sentence))

    deduped: List[Rule] = []
    seen = set()
    for rule in rules:
        key = (rule.category, rule.evidence)
        if key not in seen:
            seen.add(key)
            deduped.append(rule)
    return deduped


def rules_to_text(rules: List[Rule]) -> str:
    if not rules:
        return "No clear rule statements were detected in the uploaded policy text. Try a document with explicit coverage, exclusion, or prior authorization language."
    lines = []
    for i, rule in enumerate(rules[:15], start=1):
        lines.append(f"Rule {i} [{rule.category}]: {rule.action}")
    return "\n".join(lines)


def rules_to_json(rules: List[Rule]) -> str:
    return json.dumps([asdict(r) for r in rules], indent=2)
