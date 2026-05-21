"""Overview dashboard page."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.ui import apply_filters, export_button, inject_theme, load_data, sidebar_filters
from src.gap_analysis import compute_gap_table
from src.visualization import demand_supply_scatter, role_bar

st.set_page_config(page_title="Overview", layout="wide")
inject_theme()

resumes, jobs, gap, _, _ = load_data()
filters = sidebar_filters(resumes, jobs)
resumes_f, jobs_f = apply_filters(resumes, jobs, filters)
if not resumes_f.empty and not jobs_f.empty:
    gap = compute_gap_table(resumes_f, jobs_f)

st.title("Market Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Resumes", f"{len(resumes_f):,}")
c2.metric("Jobs", f"{len(jobs_f):,}")
c3.metric("Locations", f"{jobs_f['location'].nunique():,}")
c4.metric("Industries", f"{jobs_f['industry'].nunique():,}")

st.plotly_chart(demand_supply_scatter(gap), use_container_width=True)
st.plotly_chart(role_bar(jobs_f if not jobs_f.empty else jobs), use_container_width=True)
st.dataframe(gap.head(30), use_container_width=True, hide_index=True)
export_button(gap, "overview_gap.csv")
