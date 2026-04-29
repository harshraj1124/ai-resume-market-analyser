"""Recommendation logic for recruitment marketing teams."""

from __future__ import annotations

import math

import pandas as pd


CHANNELS = {
    "GenAI": ["LinkedIn", "GitHub", "Twitter/X", "AI meetups", "Naukri premium"],
    "Cybersecurity": ["LinkedIn", "Security forums", "GitHub", "Nullcon communities", "Referral campaigns"],
    "Cloud Security": ["LinkedIn", "Naukri", "AWS community groups", "GitHub"],
    "Kubernetes": ["GitHub", "CNCF communities", "LinkedIn", "Naukri"],
}


def channels_for_skill(skill: str) -> list[str]:
    """Return sourcing channels for a skill."""
    return CHANNELS.get(skill, ["LinkedIn", "Naukri", "Indeed India", "GitHub", "Referral campaigns"])


def recommendation_copy(skill: str, category: str) -> str:
    """Generate job ad copy tailored to shortage severity."""
    urgency = "critical growth" if "CRITICAL" in category else "high-impact"
    return (
        f"Build {urgency} teams working on {skill}. Join a product-focused environment with modern tooling, "
        "clear ownership, competitive India-market compensation, and flexible hybrid options."
    )


def build_recommendations(gap_table: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """Create actionable sourcing recommendations from gap results."""
    rows = []
    for _, row in gap_table.head(top_n).iterrows():
        skill = str(row["skill"])
        demand = int(row["demand_count"])
        supply = int(row["supply_count"])
        shortage = max(demand - supply, 0)
        estimated_fills = max(1, math.ceil(shortage * 0.28)) if shortage else max(1, math.ceil(demand * 0.08))
        rows.append(
            {
                "skill": skill,
                "gap_category": row["gap_category"],
                "gap_score": round(float(row["gap_score"]), 3),
                "target_channels": ", ".join(channels_for_skill(skill)),
                "campaign_action": f"Launch a 21-day sourcing sprint for {skill} across priority India hubs.",
                "sample_job_ad_copy": recommendation_copy(skill, str(row["gap_category"])),
                "estimated_impact": f"Could fill {estimated_fills} roles in 60 days",
                "priority": "P0" if row["gap_score"] > 0.6 else "P1" if row["gap_score"] > 0.3 else "P2",
            }
        )
    return pd.DataFrame(rows)
