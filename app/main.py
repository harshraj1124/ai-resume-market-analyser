"""Streamlit entry point."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui import apply_filters, export_button, inject_theme, load_data, sidebar_filters
from src.gap_analysis import compute_gap_table
from src.recommender import build_recommendations
from src.visualization import demand_supply_scatter, gap_bar, role_bar

st.set_page_config(page_title="AI Resume Market Analyzer", page_icon="AI", layout="wide")
inject_theme()

resumes, jobs, gap, location_gap, recommendations = load_data()
filters = sidebar_filters(resumes, jobs)
resumes_f, jobs_f = apply_filters(resumes, jobs, filters)

if not resumes_f.empty and not jobs_f.empty:
    gap = compute_gap_table(resumes_f, jobs_f)
    recommendations = build_recommendations(gap)

st.title("AI Resume Sourcing & Labor Market Demand Analyzer")
st.caption("India-first supply, demand, skill shortage, and recruitment marketing intelligence.")

cols = st.columns(4)
cols[0].metric("Candidate Supply", f"{len(resumes_f):,}")
cols[1].metric("Open Demand", f"{len(jobs_f):,}")
cols[2].metric("Critical Skills", f"{(gap['gap_category'] == 'CRITICAL SHORTAGE FIRE').sum():,}")
cols[3].metric("Median Gap", f"{gap['gap_score'].median():.2f}")

left, right = st.columns([1.25, 1])
with left:
    st.plotly_chart(gap_bar(gap), use_container_width=True)
with right:
    st.plotly_chart(demand_supply_scatter(gap), use_container_width=True)

st.plotly_chart(role_bar(jobs_f if not jobs_f.empty else jobs), use_container_width=True)

st.subheader("Top Recommendations")
st.dataframe(recommendations, use_container_width=True, hide_index=True)
export_button(recommendations, "recommendations.csv")

st.subheader("Filtered Gap Table")
st.dataframe(gap, use_container_width=True, hide_index=True)
export_button(gap, "skill_gap.csv")
