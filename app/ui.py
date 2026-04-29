"""Shared Streamlit UI helpers."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_generator import GeneratorConfig, generate_all
from main_pipeline import run_pipeline

DATA = ROOT / "data"


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --accent: #00ff9d; }
        .stApp { background: #07100d; }
        [data-testid="stMetricValue"] { color: var(--accent); }
        .block-container { padding-top: 1.5rem; }
        div[data-testid="stToolbar"] { visibility: hidden; height: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed = DATA / "processed"
    if not (processed / "skill_gap.parquet").exists():
        generate_all(GeneratorConfig(resumes=2500, jobs=1200, output_dir=DATA / "synthetic"))
        run_pipeline()
    return (
        pd.read_parquet(processed / "resumes_clean.parquet"),
        pd.read_parquet(processed / "jobs_clean.parquet"),
        pd.read_parquet(processed / "skill_gap.parquet"),
        pd.read_parquet(processed / "location_gap.parquet"),
        pd.read_parquet(processed / "recommendations.parquet"),
    )


def sidebar_filters(resumes: pd.DataFrame, jobs: pd.DataFrame) -> dict[str, object]:
    st.sidebar.title("Market Controls")
    theme = st.sidebar.toggle("Light mode", value=False)
    locations = sorted(set(resumes["location"]).union(set(jobs["location"])))
    industries = sorted(set(resumes["industry"]).union(set(jobs["industry"])))
    selected_locations = st.sidebar.multiselect("Locations", locations, default=locations[:6])
    selected_industries = st.sidebar.multiselect("Industries", industries, default=industries[:5])
    min_exp, max_exp = st.sidebar.slider("Experience band", 0, 20, (1, 12))
    st.sidebar.caption("Last analyzed: less than 1 hour ago")
    return {
        "theme": "plotly_white" if theme else "plotly_dark",
        "locations": selected_locations,
        "industries": selected_industries,
        "experience": (min_exp, max_exp),
    }


def apply_filters(resumes: pd.DataFrame, jobs: pd.DataFrame, filters: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame]:
    locations = filters["locations"]
    industries = filters["industries"]
    min_exp, max_exp = filters["experience"]
    filtered_resumes = resumes[
        resumes["location"].isin(locations)
        & resumes["industry"].isin(industries)
        & resumes["experience_years"].between(min_exp, max_exp)
    ]
    filtered_jobs = jobs[
        jobs["location"].isin(locations)
        & jobs["industry"].isin(industries)
        & (jobs["min_experience"] <= max_exp)
        & (jobs["max_experience"] >= min_exp)
    ]
    return filtered_resumes, filtered_jobs


def export_button(df: pd.DataFrame, filename: str) -> None:
    st.download_button("Export CSV", df.to_csv(index=False), file_name=filename, mime="text/csv")
