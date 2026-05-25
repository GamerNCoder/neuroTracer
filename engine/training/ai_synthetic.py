"""
Synthetic AI-style text for local training (no API keys).

Transforms human excerpts into uniform, template-heavy prose similar to LLM output.
"""

from __future__ import annotations

import random
import re
from typing import List

AI_OPENERS = [
    "In today's rapidly evolving landscape, ",
    "It is important to note that ",
    "Furthermore, ",
    "When considering this topic, ",
    "This comprehensive overview explores ",
]

AI_CLOSERS = [
    " In conclusion, this approach offers a robust framework for understanding the subject.",
    " Ultimately, leveraging these insights can drive meaningful outcomes.",
    " By following best practices, stakeholders can achieve sustainable results.",
]

AI_CONNECTORS = [
    "Additionally, ",
    "Moreover, ",
    "On the other hand, ",
    "As a result, ",
]

# Curated static AI-like samples (no network)
STATIC_AI_SAMPLES: List[str] = [
    (
        "The implementation of this solution requires a systematic approach that addresses "
        "multiple key considerations. First, we must analyze the core requirements and identify "
        "potential challenges. Second, we should develop a comprehensive strategy that accounts "
        "for various edge cases. Finally, we will implement the solution using best practices "
        "and ensure proper testing. This methodology ensures optimal results."
    ),
    (
        "Understanding the fundamentals is essential for success. The process involves several "
        "critical steps that must be executed in sequence. Each phase builds upon the previous one, "
        "creating a cohesive framework. Stakeholders should remain aligned throughout the journey "
        "to maximize efficiency and minimize risk."
    ),
    (
        "This guide provides a detailed exploration of the topic at hand. We will examine the "
        "primary components, discuss common pitfalls, and highlight strategies for improvement. "
        "Whether you are a beginner or an experienced professional, these principles remain "
        "universally applicable and easy to integrate into existing workflows."
    ),
]


def _uniform_sentences(text: str, target_len: int = 22) -> str:
    """Split into chunks of roughly equal word count (AI-like rhythm)."""
    words = text.split()
    if len(words) < 40:
        return text
    chunks: List[str] = []
    i = 0
    while i < len(words):
        chunk = words[i : i + target_len]
        if len(chunk) >= 8:
            s = " ".join(chunk).strip()
            if s and s[0].islower():
                s = s[0].upper() + s[1:]
            if s and s[-1] not in ".!?":
                s += "."
            chunks.append(s)
        i += target_len
    return " ".join(chunks)


def stylize_as_ai(human_text: str, *, seed: int | None = None) -> str:
    """
    Heuristic rewrite: formal tone, uniform cadence, AI discourse markers.
    """
    rng = random.Random(seed)
    t = re.sub(r"\s+", " ", human_text).strip()
    if len(t) > 1200:
        t = t[:1200].rsplit(" ", 1)[0] + "..."

    # Remove informal contractions
    t = re.sub(r"\bI'm\b", "I am", t, flags=re.I)
    t = re.sub(r"\bI've\b", "I have", t, flags=re.I)
    t = re.sub(r"\bdon't\b", "do not", t, flags=re.I)
    t = re.sub(r"\bcan't\b", "cannot", t, flags=re.I)
    t = re.sub(r"\bwon't\b", "will not", t, flags=re.I)
    t = re.sub(r"\bit's\b", "it is", t, flags=re.I)
    t = re.sub(r"\bmaybe\b", "potentially", t, flags=re.I)
    t = re.sub(r"\bperhaps\b", "it is possible that", t, flags=re.I)

    body = _uniform_sentences(t)
    parts = [rng.choice(AI_OPENERS) + body[:1].lower() + body[1:] if body else body]
    mid = max(1, len(body.split(".")) // 2)
    sentences = [s.strip() for s in body.split(".") if s.strip()]
    if len(sentences) >= 3:
        insert_at = min(len(sentences) - 1, mid)
        sentences[insert_at] = rng.choice(AI_CONNECTORS) + sentences[insert_at][0].lower() + sentences[insert_at][1:]
    parts = [". ".join(sentences) + ("." if sentences else "")]
    out = parts[0] + rng.choice(AI_CLOSERS)
    return re.sub(r"\s+", " ", out).strip()


def build_ai_corpus(
    human_texts: List[str],
    *,
    target_count: int | None = None,
    include_static: bool = True,
) -> List[str]:
    """
    Match human count with stylized pairs + static AI paragraphs.
    """
    n = target_count or len(human_texts)
    out: List[str] = []
    if include_static:
        out.extend(STATIC_AI_SAMPLES)
    for i, ht in enumerate(human_texts):
        if len(out) >= n:
            break
        out.append(stylize_as_ai(ht, seed=i))
    # Pad with repeated stylized if needed
    idx = 0
    while len(out) < n and human_texts:
        out.append(stylize_as_ai(human_texts[idx % len(human_texts)], seed=10000 + idx))
        idx += 1
    return out[:n]
