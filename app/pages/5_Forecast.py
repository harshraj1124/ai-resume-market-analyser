"""Skill Demand Forecast page — forward-looking market intelligence."""

from __future__ import annotations

import streamlit as st

from app.ui import apply_filters, export_button, inject_theme, load_data, sidebar_filters
from src.forecaster import chart_data, forecast_table, growth_ranking
from src.visualization import forecast_chart, growth_bar

st.set_page_config(page_title="Demand Forecast", layout="wide")
inject_theme()

resumes, jobs, _, _, _ = load_data()
filters = sidebar_filters(resumes, jobs)
_, jobs_f = apply_filters(resumes, jobs, filters)
jobs_view = jobs_f if not jobs_f.empty else jobs

st.title("Skill Demand Forecast")
st.caption(
    "Linear trend extrapolation on historical job postings. "
    "Solid lines = observed data. Dotted lines = 6-month projection."
)

with st.spinner("Computing forecasts…"):
    cd = chart_data(jobs_view, top_n=8, forecast_months=6)
    ft = forecast_table(jobs_view, top_n=12, horizons=[3, 6, 12])
    gr = growth_ranking(jobs_view, top_n=15)

st.plotly_chart(forecast_chart(cd), use_container_width=True)

st.divider()
col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("Growth Velocity")
    st.caption("Monthly rate of new job postings per skill (linear slope).")
    st.plotly_chart(growth_bar(gr), use_container_width=True)

with col_b:
    st.subheader("12-Month Outlook")
    if not ft.empty:
        pivot = ft[ft["horizon_months"] == 12][
            ["skill", "forecasted_demand", "trend_slope", "current_demand", "r2_score"]
        ].sort_values("forecasted_demand", ascending=False)
        pivot.columns = ["Skill", "Forecast (12m)", "Monthly Slope", "Current Demand", "R²"]
        st.dataframe(pivot, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Full Forecast Table (3 / 6 / 12 months)")
if not ft.empty:
    display = ft.rename(
        columns={
            "skill": "Skill",
            "horizon_months": "Horizon (months)",
            "period": "Target Month",
            "forecasted_demand": "Forecasted Demand",
            "trend_slope": "Monthly Slope",
            "current_demand": "Current Demand",
            "avg_monthly_demand": "Avg Monthly",
            "r2_score": "R²",
        }
    )
    st.dataframe(display, use_container_width=True, hide_index=True)
    export_button(ft, "skill_forecast.csv")
else:
    st.info("Not enough historical data points to compute forecasts. Try generating more data.")

st.caption(
    "Model: Ordinary Least Squares linear regression on monthly unique job-posting counts per skill. "
    "R² values above 0.7 indicate reliable trends."
)
