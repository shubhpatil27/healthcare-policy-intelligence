from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .document_io import Chunk


@dataclass
class Answer:
    answer: str
    sources: List[Tuple[str, float, str]]


def build_index(chunks: List[Chunk]):
    corpus = [c.text for c in chunks]
    if not corpus:
        return None, None, []
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix, chunks


def _extractive_answer(question: str, ranked_chunks: List[str]) -> str:
    question_terms = [t for t in question.lower().split() if len(t) > 3]
    text = " ".join(ranked_chunks)
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    scored = []
    for s in sentences:
        s_low = s.lower()
        score = sum(1 for t in question_terms if t in s_low)
        if score:
            scored.append((score, s))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [s for _, s in scored[:3]]
        out = ". ".join(top).strip()
        return out + ("." if not out.endswith(".") else "")
    preview = " ".join(ranked_chunks)[:550]
    return preview + ("..." if len(preview) == 550 else "")


def answer_question(question: str, vectorizer, matrix, chunks: List[Chunk], top_k: int = 4) -> Answer:
    if not chunks or vectorizer is None or matrix is None:
        return Answer("No extracted text available to search.", [])

    q_vec = vectorizer.transform([question])
    sims = cosine_similarity(q_vec, matrix).flatten()
    ranked_idx = sims.argsort()[::-1][:top_k]

    sources: List[Tuple[str, float, str]] = []
    ranked_chunks: List[str] = []
    for idx in ranked_idx:
        score = float(sims[idx])
        if score <= 0:
            continue
        chunk = chunks[idx]
        label = f"{chunk.source} · chunk {chunk.chunk_id}"
        sources.append((label, score, chunk.text))
        ranked_chunks.append(chunk.text)

    if not sources:
        return Answer(
            "I could not find a strong match in the uploaded document. Try asking with terms that appear in the policy, such as a CPT code, coverage phrase, or prior authorization keyword.",
            [],
        )

    answer = _extractive_answer(question, ranked_chunks)
    return Answer(answer, sources)
