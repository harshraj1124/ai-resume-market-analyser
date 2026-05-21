"""Supply-demand gap page."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.ui import apply_filters, export_button, inject_theme, load_data, sidebar_filters
from src.gap_analysis import compute_gap_table, location_gap
from src.visualization import gap_bar, heatmap

st.set_page_config(page_title="Supply Demand Gap", layout="wide")
inject_theme()

resumes, jobs, gap, loc_gap, _ = load_data()
filters = sidebar_filters(resumes, jobs)
resumes_f, jobs_f = apply_filters(resumes, jobs, filters)
if not resumes_f.empty and not jobs_f.empty:
    gap = compute_gap_table(resumes_f, jobs_f)
    loc_gap = location_gap(resumes_f, jobs_f)

st.title("Supply Demand Gap")
st.plotly_chart(gap_bar(gap, limit=30), use_container_width=True)
top_skills = gap.head(12)["skill"].tolist()
st.plotly_chart(heatmap(loc_gap, top_skills), use_container_width=True)
st.dataframe(gap, use_container_width=True, hide_index=True)
export_button(gap, "supply_demand_gap.csv")
