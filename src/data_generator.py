"""Synthetic supply and demand data generation."""

from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    from faker import Faker
except ImportError:  # pragma: no cover - exercised only in minimal environments
    Faker = None

LOGGER = logging.getLogger(__name__)

INDIAN_LOCATIONS = [
    "Bangalore",
    "Hyderabad",
    "Delhi NCR",
    "Pune",
    "Chennai",
    "Mumbai",
    "Gurugram",
    "Noida",
    "Kochi",
    "Ahmedabad",
    "Jaipur",
    "Coimbatore",
]

GLOBAL_LOCATIONS = ["Singapore", "London", "Berlin", "Dubai", "New York", "Toronto"]

INDUSTRIES = [
    "SaaS",
    "BFSI",
    "IT Services",
    "E-commerce",
    "Healthcare",
    "Telecom",
    "Manufacturing",
    "EdTech",
    "Retail",
    "Cybersecurity",
]

ROLE_FAMILIES = {
    "AI Engineer": ["Python", "GenAI", "LLMs", "LangChain", "PyTorch", "Vector Databases", "MLOps"],
    "Data Scientist": ["Python", "SQL", "scikit-learn", "TensorFlow", "Statistics", "Tableau"],
    "Data Engineer": ["Python", "SQL", "Spark", "Airflow", "Databricks", "AWS"],
    "Cloud Engineer": ["AWS", "Azure", "GCP", "Kubernetes", "Terraform", "Docker"],
    "Cybersecurity Analyst": ["Cybersecurity", "SIEM", "IAM", "Cloud Security", "Network Security"],
    "Full Stack Engineer": ["JavaScript", "React", "Node.js", "Python", "SQL", "Docker"],
    "Backend Engineer": ["Java", "Python", "Go", "Microservices", "Kafka", "SQL"],
    "DevOps Engineer": ["Kubernetes", "Docker", "Terraform", "Jenkins", "AWS", "Observability"],
    "Product Analyst": ["SQL", "Power BI", "Tableau", "Python", "Experimentation"],
    "Blockchain Engineer": ["Blockchain", "Solidity", "Rust", "Smart Contracts", "Web3"],
}

SKILL_TAXONOMY = {
    "Programming": ["Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "Scala", "Kotlin"],
    "Cloud": ["AWS", "Azure", "GCP", "Kubernetes", "Docker", "Terraform", "Cloud Security", "FinOps"],
    "AI/ML": ["TensorFlow", "PyTorch", "scikit-learn", "LangChain", "GenAI", "LLMs", "MLOps", "RAG", "Vector Databases"],
    "Data": ["SQL", "Spark", "Airflow", "Databricks", "Snowflake", "Tableau", "Power BI", "dbt"],
    "Cybersecurity": ["Cybersecurity", "SIEM", "IAM", "AppSec", "DevSecOps", "Network Security", "Zero Trust"],
    "DevOps": ["Jenkins", "GitHub Actions", "Observability", "Prometheus", "Grafana", "Linux"],
    "Frontend": ["React", "Angular", "Vue", "Next.js", "HTML", "CSS"],
    "Backend": ["Node.js", "Django", "FastAPI", "Spring Boot", "Microservices", "Kafka"],
    "Blockchain": ["Blockchain", "Solidity", "Smart Contracts", "Web3"],
    "Soft Skills": ["Communication", "Leadership", "Stakeholder Management", "Mentoring", "Problem Solving"],
    "Emerging Tech": ["Quantum", "Sustainability AI", "Privacy Engineering", "Edge AI", "Responsible AI"],
}

SHORTAGE_SKILLS = {"GenAI", "LLMs", "LangChain", "MLOps", "Cloud Security", "Cybersecurity", "Kubernetes", "RAG"}


class SimpleFaker:
    """Small fallback used when the optional faker package is not installed yet."""

    first_names = ["Aarav", "Diya", "Ishaan", "Meera", "Kabir", "Ananya", "Rohan", "Priya"]
    last_names = ["Sharma", "Iyer", "Khan", "Nair", "Reddy", "Das", "Patel", "Menon"]
    company_words = ["Nexa", "Prism", "Astra", "Kite", "Zenith", "Orbit", "FinEdge", "CloudWorks"]

    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)

    def name(self) -> str:
        return f"{self.rng.choice(self.first_names)} {self.rng.choice(self.last_names)}"

    def company(self) -> str:
        return f"{self.rng.choice(self.company_words)} Technologies"


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for synthetic market generation."""

    resumes: int = 15_000
    jobs: int = 8_000
    seed: int = 42
    output_dir: Path = Path("data/synthetic")


def write_taxonomy(output_dir: Path) -> Path:
    """Write the project skill taxonomy as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "skills_taxonomy.json"
    path.write_text(json.dumps(SKILL_TAXONOMY, indent=2), encoding="utf-8")
    return path


def _weighted_location(rng: np.random.Generator) -> str:
    locations = INDIAN_LOCATIONS + GLOBAL_LOCATIONS
    weights = np.array([0.16, 0.13, 0.11, 0.10, 0.09, 0.08, 0.08, 0.07, 0.04, 0.04, 0.03, 0.03, 0.01, 0.01, 0.01, 0.01, 0.005, 0.005])
    weights = weights / weights.sum()
    return str(rng.choice(locations, p=weights))


def _sample_skills(role: str, rng: np.random.Generator, demand_side: bool) -> list[str]:
    base = list(ROLE_FAMILIES[role])
    all_skills = sorted({skill for skills in SKILL_TAXONOMY.values() for skill in skills})
    if demand_side:
        extra_pool = all_skills + list(SHORTAGE_SKILLS) * 4
        count = int(rng.integers(5, 9))
    else:
        extra_pool = [skill for skill in all_skills if skill not in SHORTAGE_SKILLS] + list(SHORTAGE_SKILLS)
        count = int(rng.integers(4, 8))
    chosen = set(rng.choice(base, size=min(len(base), 3), replace=False).tolist())
    while len(chosen) < count:
        chosen.add(str(rng.choice(extra_pool)))
    return sorted(chosen)


def _resume_text(name: str, role: str, skills: Iterable[str], experience: int, location: str) -> str:
    return (
        f"{name}\n{role} based in {location}\n"
        f"{experience} years of experience across {', '.join(skills)}.\n"
        "Delivered measurable hiring, platform, analytics, and automation outcomes for enterprise teams."
    )


def generate_resumes(config: GeneratorConfig) -> pd.DataFrame:
    """Generate candidate supply records."""
    fake = Faker("en_IN") if Faker is not None else SimpleFaker(config.seed)
    rng = np.random.default_rng(config.seed)
    records = []
    roles = list(ROLE_FAMILIES)

    for idx in range(config.resumes):
        role = str(rng.choice(roles))
        skills = _sample_skills(role, rng, demand_side=False)
        experience = int(max(0, rng.normal(5.8, 3.2)))
        location = _weighted_location(rng)
        name = fake.name()
        salary_lpa = round(float(max(4, rng.normal(18 + experience * 1.8, 7))), 1)
        records.append(
            {
                "candidate_id": f"CAN-{idx + 1:06d}",
                "name": name,
                "role": role,
                "location": location,
                "industry": str(rng.choice(INDUSTRIES)),
                "experience_years": experience,
                "expected_salary_lpa": salary_lpa,
                "skills": skills,
                "resume_text": _resume_text(name, role, skills, experience, location),
                "source_channel": str(rng.choice(["LinkedIn", "Naukri", "GitHub", "Referral", "Indeed India"])),
                "available_from": pd.Timestamp("2025-01-01") + pd.to_timedelta(int(rng.integers(0, 520)), unit="D"),
            }
        )
    return pd.DataFrame(records)


def generate_jobs(config: GeneratorConfig) -> pd.DataFrame:
    """Generate demand-side job posting records."""
    fake = Faker("en_IN") if Faker is not None else SimpleFaker(config.seed + 7)
    rng = np.random.default_rng(config.seed + 7)
    records = []
    roles = list(ROLE_FAMILIES)
    role_weights = np.array([0.14, 0.11, 0.12, 0.12, 0.10, 0.14, 0.10, 0.10, 0.05, 0.02])
    role_weights = role_weights / role_weights.sum()

    for idx in range(config.jobs):
        role = str(rng.choice(roles, p=role_weights))
        skills = _sample_skills(role, rng, demand_side=True)
        min_exp = int(rng.integers(1, 8))
        max_exp = int(min_exp + rng.integers(2, 7))
        location = _weighted_location(rng)
        salary_min = round(float(max(6, rng.normal(14 + min_exp * 2.2, 5))), 1)
        salary_max = round(float(salary_min + rng.normal(12, 5)), 1)
        records.append(
            {
                "job_id": f"JOB-{idx + 1:06d}",
                "title": role,
                "company": fake.company(),
                "location": location,
                "industry": str(rng.choice(INDUSTRIES)),
                "min_experience": min_exp,
                "max_experience": max_exp,
                "salary_min_lpa": salary_min,
                "salary_max_lpa": max(salary_max, salary_min + 2),
                "required_skills": skills,
                "posting_text": f"Hiring {role} in {location}. Required skills: {', '.join(skills)}.",
                "source": str(rng.choice(["Naukri", "LinkedIn India", "Indeed India", "Company Careers", "Instahyre"])),
                "posted_at": pd.Timestamp("2025-01-01") + pd.to_timedelta(int(rng.integers(0, 520)), unit="D"),
                "openings": int(rng.integers(1, 8)),
            }
        )
    return pd.DataFrame(records)


def persist_datasets(resumes: pd.DataFrame, jobs: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    """Persist synthetic datasets in parquet and JSONL formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "resumes_parquet": output_dir / "resumes.parquet",
        "jobs_parquet": output_dir / "jobs.parquet",
        "resumes_json": output_dir / "resumes.jsonl",
        "jobs_json": output_dir / "jobs.jsonl",
    }
    resumes.to_parquet(paths["resumes_parquet"], index=False)
    jobs.to_parquet(paths["jobs_parquet"], index=False)
    resumes.to_json(paths["resumes_json"], orient="records", lines=True, date_format="iso")
    jobs.to_json(paths["jobs_json"], orient="records", lines=True, date_format="iso")
    write_taxonomy(output_dir)
    return paths


def generate_all(config: GeneratorConfig) -> dict[str, Path]:
    """Generate and save all synthetic assets."""
    random.seed(config.seed)
    np.random.seed(config.seed)
    LOGGER.info("Generating %s resumes and %s jobs", config.resumes, config.jobs)
    resumes = generate_resumes(config)
    jobs = generate_jobs(config)
    return persist_datasets(resumes, jobs, config.output_dir)
