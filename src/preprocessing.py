"""Data loading, validation, and normalization utilities."""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


def read_dataset(path: Path) -> pd.DataFrame:
    """Read a parquet, JSONL, or CSV dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix in {".jsonl", ".json"}:
        return pd.read_json(path, lines=path.suffix == ".jsonl")
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported dataset type: {path.suffix}")


def parse_list(value: Any) -> list[str]:
    """Normalize a scalar or serialized list into a list of strings."""
    if isinstance(value, (list, tuple, np.ndarray)):
        return [str(item).strip() for item in value if str(item).strip()]
    if pd.isna(value):
        return []
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (SyntaxError, ValueError):
                LOGGER.debug("Could not parse list value: %s", text)
        return [part.strip() for part in text.split(",") if part.strip()]
    return [str(value).strip()]


def normalize_frame(df: pd.DataFrame, skill_column: str) -> pd.DataFrame:
    """Normalize common fields and skill lists."""
    frame = df.copy()
    if skill_column not in frame.columns:
        raise KeyError(f"Missing skill column: {skill_column}")
    frame[skill_column] = frame[skill_column].apply(parse_list)
    for column in ["location", "industry", "role", "title"]:
        if column in frame.columns:
            frame[column] = frame[column].fillna("Unknown").astype(str).str.strip()
    for column in ["posted_at", "available_from"]:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def explode_skills(df: pd.DataFrame, skill_column: str, entity_id: str, value_name: str = "skill") -> pd.DataFrame:
    """Explode a dataframe from list skills into one row per entity-skill pair."""
    frame = normalize_frame(df, skill_column)
    exploded = frame[[entity_id, skill_column] + [c for c in ["location", "industry"] if c in frame.columns]].explode(skill_column)
    exploded = exploded.rename(columns={skill_column: value_name})
    exploded[value_name] = exploded[value_name].fillna("").astype(str).str.strip()
    return exploded[exploded[value_name] != ""]


def save_processed(df: pd.DataFrame, path: Path) -> Path:
    """Save a processed dataframe as parquet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path
