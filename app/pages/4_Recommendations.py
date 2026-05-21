"""Recruitment recommendations page."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.ui import apply_filters, export_button, inject_theme, load_data, sidebar_filters
from src.gap_analysis import compute_gap_table
from src.recommender import build_recommendations
from src.visualization import sankey_skill_channel

st.set_page_config(page_title="Recommendations", layout="wide")
inject_theme()

resumes, jobs, gap, _, recommendations = load_data()
filters = sidebar_filters(resumes, jobs)
resumes_f, jobs_f = apply_filters(resumes, jobs, filters)
if not resumes_f.empty and not jobs_f.empty:
    gap = compute_gap_table(resumes_f, jobs_f)
    recommendations = build_recommendations(gap, top_n=15)

st.title("Recruitment Marketing Recommendations")
st.plotly_chart(sankey_skill_channel(recommendations), use_container_width=True)

for _, row in recommendations.head(8).iterrows():
    with st.container(border=True):
        c1, c2 = st.columns([0.35, 0.65])
        c1.metric(row["skill"], row["priority"])
        c1.write(row["gap_category"])
        c2.write(row["campaign_action"])
        c2.code(row["sample_job_ad_copy"], language="text")
        c2.caption(row["estimated_impact"])

st.dataframe(recommendations, use_container_width=True, hide_index=True)
export_button(recommendations, "recommendations.csv")
