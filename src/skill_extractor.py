"""Skill extraction using taxonomy rules with optional spaCy phrase matching."""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def load_taxonomy(path: Path) -> dict[str, list[str]]:
    """Load a skill taxonomy from JSON."""
    if not path.exists():
        raise FileNotFoundError(f"Taxonomy not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_taxonomy(taxonomy: dict[str, list[str]]) -> list[str]:
    """Return unique skills from all taxonomy categories."""
    return sorted({skill for skills in taxonomy.values() for skill in skills}, key=len, reverse=True)


@lru_cache(maxsize=1)
def _load_spacy_model() -> object | None:
    """Load spaCy model if available; extraction still works without it."""
    try:
        import spacy

        return spacy.load("en_core_web_lg")
    except Exception as exc:  # pragma: no cover - depends on local model availability
        LOGGER.info("spaCy model unavailable, using taxonomy regex extraction: %s", exc)
        return None


class SkillExtractor:
    """Extract normalized skills from free text."""

    def __init__(self, taxonomy: dict[str, list[str]], use_spacy: bool = True) -> None:
        self.taxonomy = taxonomy
        self.skills = flatten_taxonomy(taxonomy)
        self.aliases = self._build_aliases(self.skills)
        self.nlp = _load_spacy_model() if use_spacy else None

    @staticmethod
    def _build_aliases(skills: list[str]) -> dict[str, str]:
        aliases = {skill.lower(): skill for skill in skills}
        aliases.update(
            {
                "large language model": "LLMs",
                "large language models": "LLMs",
                "generative ai": "GenAI",
                "rag": "RAG",
                "k8s": "Kubernetes",
                "postgres": "SQL",
                "postgresql": "SQL",
                "react.js": "React",
                "nodejs": "Node.js",
            }
        )
        return aliases

    def extract(self, text: str) -> list[str]:
        """Extract skills from text and return canonical names."""
        if not text:
            return []
        lowered = text.lower()
        found: set[str] = set()
        for alias, canonical in self.aliases.items():
            pattern = r"(?<![a-z0-9+#])" + re.escape(alias) + r"(?![a-z0-9+#])"
            if re.search(pattern, lowered):
                found.add(canonical)
        if self.nlp is not None:  # pragma: no cover
            doc = self.nlp(text[:50_000])
            for chunk in doc.noun_chunks:
                normalized = chunk.text.lower().strip()
                if normalized in self.aliases:
                    found.add(self.aliases[normalized])
        return sorted(found)

    def categorize(self, skill: str) -> str:
        """Return taxonomy category for a skill."""
        for category, skills in self.taxonomy.items():
            if skill in skills:
                return category
        return "Other"
