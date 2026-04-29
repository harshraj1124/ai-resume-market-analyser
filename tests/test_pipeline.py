"""End-to-end checks for the resume market analysis pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_generator import GeneratorConfig, generate_jobs, generate_resumes, write_taxonomy
from src.gap_analysis import categorize_gap, compute_gap_table
from src.recommender import build_recommendations
from src.skill_extractor import SkillExtractor, load_taxonomy


def test_gap_formula_and_recommendations() -> None:
    config = GeneratorConfig(resumes=200, jobs=120, seed=11)
    resumes = generate_resumes(config)
    jobs = generate_jobs(config)
    gap = compute_gap_table(resumes, jobs)
    assert not gap.empty
    first = gap.iloc[0]
    expected = (first["demand_count"] - first["supply_count"]) / (first["demand_count"] + 1)
    assert first["gap_score"] == expected
    assert categorize_gap(0.7) == "CRITICAL SHORTAGE FIRE"
    recommendations = build_recommendations(gap, top_n=5)
    assert len(recommendations) == 5
    assert {"target_channels", "sample_job_ad_copy", "estimated_impact"}.issubset(recommendations.columns)


def test_skill_extractor_taxonomy(tmp_path: Path) -> None:
    taxonomy_path = write_taxonomy(tmp_path)
    taxonomy = load_taxonomy(taxonomy_path)
    extractor = SkillExtractor(taxonomy, use_spacy=False)
    skills = extractor.extract("Built Generative AI systems with Python, LangChain, AWS, and k8s.")
    assert "GenAI" in skills
    assert "Python" in skills
    assert "LangChain" in skills
    assert "AWS" in skills
    assert "Kubernetes" in skills
