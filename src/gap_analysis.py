"""Supply-demand gap scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.frequency_analysis import skill_frequency


def categorize_gap(score: float) -> str:
    """Categorize a numeric gap score."""
    if score > 0.6:
        return "CRITICAL SHORTAGE FIRE"
    if score > 0.3:
        return "HIGH DEMAND"
    if score > -0.2:
        return "BALANCED"
    return "SUPPLY SURPLUS"


def compute_gap_table(resumes: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    """Compute skill-level supply-demand gaps."""
    supply = skill_frequency(resumes, "skills", "candidate_id", "supply_count")
    demand = skill_frequency(jobs, "required_skills", "job_id", "demand_count")
    gap = demand.merge(supply, on="skill", how="outer").fillna(0)
    gap["supply_count"] = gap["supply_count"].astype(int)
    gap["demand_count"] = gap["demand_count"].astype(int)
    gap["gap_score"] = (gap["demand_count"] - gap["supply_count"]) / (gap["demand_count"] + 1)
    gap["gap_category"] = gap["gap_score"].apply(categorize_gap)
    gap["market_pressure"] = np.where(gap["demand_count"] > 0, gap["demand_count"] / (gap["supply_count"] + 1), 0)
    return gap.sort_values(["gap_score", "demand_count"], ascending=[False, False]).reset_index(drop=True)


def location_gap(resumes: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    """Compute location and skill-level gaps."""
    supply = resumes.explode("skills").groupby(["location", "skills"], as_index=False)["candidate_id"].nunique()
    demand = jobs.explode("required_skills").groupby(["location", "required_skills"], as_index=False)["job_id"].nunique()
    supply = supply.rename(columns={"skills": "skill", "candidate_id": "supply_count"})
    demand = demand.rename(columns={"required_skills": "skill", "job_id": "demand_count"})
    frame = demand.merge(supply, on=["location", "skill"], how="outer").fillna(0)
    frame["gap_score"] = (frame["demand_count"] - frame["supply_count"]) / (frame["demand_count"] + 1)
    frame["gap_category"] = frame["gap_score"].apply(categorize_gap)
    return frame.sort_values("gap_score", ascending=False)
