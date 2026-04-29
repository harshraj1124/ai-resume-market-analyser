"""Frequency analysis for resume supply and job demand."""

from __future__ import annotations

import pandas as pd

from src.preprocessing import explode_skills


def skill_frequency(df: pd.DataFrame, skill_column: str, entity_id: str, count_name: str) -> pd.DataFrame:
    """Count unique entities per skill."""
    exploded = explode_skills(df, skill_column, entity_id)
    return (
        exploded.groupby("skill", as_index=False)[entity_id]
        .nunique()
        .rename(columns={entity_id: count_name})
        .sort_values(count_name, ascending=False)
    )


def grouped_skill_frequency(
    df: pd.DataFrame,
    skill_column: str,
    entity_id: str,
    group_columns: list[str],
    count_name: str,
) -> pd.DataFrame:
    """Count unique entities per skill and grouping columns."""
    exploded = explode_skills(df, skill_column, entity_id)
    groups = group_columns + ["skill"]
    return exploded.groupby(groups, as_index=False)[entity_id].nunique().rename(columns={entity_id: count_name})


def role_frequency(df: pd.DataFrame, role_column: str, count_column: str, count_name: str) -> pd.DataFrame:
    """Count records by role/title."""
    return df.groupby(role_column, as_index=False)[count_column].nunique().rename(columns={count_column: count_name})
