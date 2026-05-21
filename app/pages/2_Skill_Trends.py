"""Skill trends page: demand/supply leaders, word cloud, salary intelligence."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.ui import apply_filters, export_button, inject_theme, load_data, sidebar_filters
from src.frequency_analysis import skill_frequency
from src.visualization import salary_box, trend_line, word_cloud_figure

st.set_page_config(page_title="Skill Trends", layout="wide")
inject_theme()

resumes, jobs, _, _, _ = load_data()
filters = sidebar_filters(resumes, jobs)
resumes_f, jobs_f = apply_filters(resumes, jobs, filters)
jobs_view = jobs_f if not jobs_f.empty else jobs
resumes_view = resumes_f if not resumes_f.empty else resumes

st.title("Skill Trends")

st.plotly_chart(trend_line(jobs_view), use_container_width=True)

st.divider()
demand = skill_frequency(jobs_view, "required_skills", "job_id", "demand_count")
supply = skill_frequency(resumes_view, "skills", "candidate_id", "supply_count")

wc_fig = word_cloud_figure(demand)
if wc_fig:
    st.plotly_chart(wc_fig, use_container_width=True)

left, right = st.columns(2)
left.subheader("Demand Leaders")
left.dataframe(demand.head(25), use_container_width=True, hide_index=True)
right.subheader("Supply Leaders")
right.dataframe(supply.head(25), use_container_width=True, hide_index=True)

st.divider()
st.subheader("Salary Intelligence by Role")
st.caption("Midpoint of offered salary range (min+max)/2 across all job postings for filtered locations/industries.")
st.plotly_chart(salary_box(jobs_view), use_container_width=True)

export_button(demand, "skill_demand.csv")
