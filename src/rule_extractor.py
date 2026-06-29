from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import re
from typing import List


@dataclass
class Rule:
    title: str
    category: str
    what_it_means: str
    applies_to: str
    evidence: str


DECISION_KEYWORDS = [
    "medically necessary",
    "not medically necessary",
    "unproven",
    "insufficient evidence",
    "coverage",
    "covered",
    "not covered",
    "benefit coverage",
    "required",
    "must",
    "shall",
    "contraindicated",
    "does not imply",
    "does not guarantee",
    "may require",
    "eligible",
    "approval",
]


EXCLUDE_SECTION_KEYWORDS = [
    "definitions",
    "description of services",
    "clinical evidence",
    "references",
    "fda",
    "revision information",
    "policy history",
    "instructions for use",
    "background",
]


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_paragraphs(text: str) -> List[str]:
    text = text.replace("\r", "\n")
    parts = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]

    # Fallback for PDFs that come in as one large block
    if len(parts) <= 1:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            return []
        parts = []
        buffer = []
        for ln in lines:
            buffer.append(ln)
            if ln.endswith(".") or ln.endswith(":"):
                parts.append(" ".join(buffer).strip())
                buffer = []
        if buffer:
            parts.append(" ".join(buffer).strip())

    return parts


def _is_noise(paragraph: str) -> bool:
    s = paragraph.lower()
    return any(k in s for k in EXCLUDE_SECTION_KEYWORDS)


def _extract_bullets(text: str) -> List[str]:
    # Pull bullet items from paragraphs like:
    # • item one • item two • item three
    items = re.findall(r"•\s*(.+?)(?=\s*•|\s*$)", text, flags=re.S)
    cleaned = []
    for item in items:
        item = _clean(item)
        item = item.strip(" .;:")
        if item:
            cleaned.append(item)
    return cleaned


def _title_case_summary(text: str) -> str:
    text = _clean(text)
    if len(text) > 90:
        text = text[:87].rstrip() + "..."
    return text


def _make_rule(title: str, category: str, what_it_means: str, applies_to: str, evidence: str) -> Rule:
    return Rule(
        title=title,
        category=category,
        what_it_means=what_it_means,
        applies_to=applies_to,
        evidence=_clean(evidence),
    )


def extract_rules(text: str) -> List[Rule]:
    paragraphs = _split_paragraphs(text)
    rules: List[Rule] = []

    for para in paragraphs:
        p = _clean(para)
        low = p.lower()

        if not p:
            continue
        if _is_noise(p):
            continue

        # 1) Not medically necessary / unproven services
        if "not medically necessary" in low or "unproven" in low:
            bullets = _extract_bullets(p)
            applies_to = "; ".join(bullets[:6]) if bullets else "The services listed in the policy"
            rules.append(
                _make_rule(
                    title="Not medically necessary services",
                    category="Coverage",
                    what_it_means="These services are considered unproven and are not covered under this policy.",
                    applies_to=applies_to,
                    evidence=p,
                )
            )
            continue

        # 2) Coverage depends on the member-specific plan
        if "benefit coverage for health services is determined" in low:
            rules.append(
                _make_rule(
                    title="Coverage depends on the member's plan",
                    category="Coverage",
                    what_it_means="This policy does not decide payment by itself. Coverage depends on the member's benefit plan and applicable laws.",
                    applies_to="All services reviewed under this policy",
                    evidence=p,
                )
            )
            continue

        # 3) Code listing does not guarantee coverage
        if "does not imply" in low or "does not guarantee" in low:
            rules.append(
                _make_rule(
                    title="Code listing does not equal coverage",
                    category="Coverage",
                    what_it_means="A CPT or HCPCS code appearing in the policy does not guarantee the service is covered or reimbursable.",
                    applies_to="Referenced procedure and diagnosis codes",
                    evidence=p,
                )
            )
            continue

        # 4) Proven and medically necessary
        if "proven and medically necessary" in low:
            rules.append(
                _make_rule(
                    title="Covered only in certain circumstances",
                    category="Coverage",
                    what_it_means="Knee surgery may be medically necessary only when the policy criteria are met.",
                    applies_to="Surgery of the knee",
                    evidence=p,
                )
            )
            continue

        # 5) Medical records may be requested
        if "medical records documentation may be required" in low:
            rules.append(
                _make_rule(
                    title="Medical records may be requested",
                    category="Documentation",
                    what_it_means="The plan may ask for medical records to check whether the criteria are met, but records alone do not guarantee coverage.",
                    applies_to="Coverage review",
                    evidence=p,
                )
            )
            continue

        # 6) FDA note
        if "fda approval alone is not a basis for coverage" in low:
            rules.append(
                _make_rule(
                    title="FDA approval is not enough",
                    category="Coverage",
                    what_it_means="FDA approval by itself does not mean the service is covered.",
                    applies_to="Devices and procedures mentioned in the policy",
                    evidence=p,
                )
            )
            continue

        # 7) Requirement language
        if any(k in low for k in ["must", "shall", "required", "eligible", "contraindicated"]):
            # Keep only if it's clearly a policy-style requirement statement
            if len(p) >= 50:
                rules.append(
                    _make_rule(
                        title=_title_case_summary(p.split(":")[0]),
                        category="Requirement",
                        what_it_means="This is a policy requirement that must be met before approval or coverage is considered.",
                        applies_to="Applicants or procedures described in the sentence",
                        evidence=p,
                    )
                )

    # Remove duplicates
    unique: List[Rule] = []
    seen = set()
    for rule in rules:
        key = (rule.title.lower(), rule.what_it_means.lower(), rule.applies_to.lower())
        if key not in seen:
            seen.add(key)
            unique.append(rule)

    return unique[:12]


def rules_to_text(rules: List[Rule]) -> str:
    if not rules:
        return "No high-confidence policy rules were extracted."

    lines = []
    for i, rule in enumerate(rules, start=1):
        lines.append(f"Rule {i} — {rule.title}")
        lines.append(f"Category: {rule.category}")
        lines.append(f"What it means: {rule.what_it_means}")
        lines.append(f"Applies to: {rule.applies_to}")
        lines.append(f"Evidence: {rule.evidence}")
        lines.append("")
    return "\n".join(lines).strip()


def rules_to_json(rules: List[Rule]) -> str:
    return json.dumps([asdict(rule) for rule in rules], indent=2)