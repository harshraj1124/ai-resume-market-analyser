"""Run the complete analysis pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from src.gap_analysis import compute_gap_table, location_gap
from src.preprocessing import normalize_frame, read_dataset, save_processed
from src.recommender import build_recommendations

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def run_pipeline() -> dict[str, Path]:
    """Load synthetic data, compute analytics, and save processed outputs."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    resumes_path = DATA / "synthetic" / "resumes.parquet"
    jobs_path = DATA / "synthetic" / "jobs.parquet"
    resumes = normalize_frame(read_dataset(resumes_path), "skills")
    jobs = normalize_frame(read_dataset(jobs_path), "required_skills")

    gap = compute_gap_table(resumes, jobs)
    loc_gap = location_gap(resumes, jobs)
    recs = build_recommendations(gap)

    outputs = {
        "resumes": save_processed(resumes, DATA / "processed" / "resumes_clean.parquet"),
        "jobs": save_processed(jobs, DATA / "processed" / "jobs_clean.parquet"),
        "gap": save_processed(gap, DATA / "processed" / "skill_gap.parquet"),
        "location_gap": save_processed(loc_gap, DATA / "processed" / "location_gap.parquet"),
        "recommendations": save_processed(recs, DATA / "processed" / "recommendations.parquet"),
    }
    for name, path in outputs.items():
        logging.info("Saved %s to %s", name, path)
    return outputs


if __name__ == "__main__":
    run_pipeline()
