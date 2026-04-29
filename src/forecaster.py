"""Skill demand forecasting using linear trend extrapolation on historical job data."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

LOGGER = logging.getLogger(__name__)


def _monthly_series(jobs: pd.DataFrame, skill: str) -> pd.Series:
    """Return a sorted monthly demand count series for a single skill."""
    frame = jobs.copy()
    frame["month_ord"] = pd.to_datetime(frame["posted_at"], errors="coerce").dt.to_period("M")
    exploded = frame.explode("required_skills")
    filtered = exploded[exploded["required_skills"] == skill]
    return filtered.groupby("month_ord")["job_id"].nunique().sort_index()


def forecast_skill(series: pd.Series, horizons: list[int]) -> pd.DataFrame:
    """Fit a linear trend on a skill's monthly demand and return point forecasts.

    Returns an empty DataFrame if fewer than 3 historical data points exist.
    """
    if len(series) < 3:
        return pd.DataFrame()
    x = np.arange(len(series), dtype=float).reshape(-1, 1)
    y = series.values.astype(float)
    model = LinearRegression().fit(x, y)
    last = series.index[-1]
    rows = []
    for h in horizons:
        period = last + h
        predicted = float(model.predict([[len(series) + h - 1]])[0])
        rows.append(
            {
                "horizon_months": h,
                "period": str(period),
                "forecasted_demand": max(0, round(predicted)),
                "trend_slope": round(float(model.coef_[0]), 3),
                "r2_score": round(float(model.score(x, y)), 3),
            }
        )
    return pd.DataFrame(rows)


def top_skills_by_demand(jobs: pd.DataFrame, top_n: int) -> list[str]:
    """Return top-N skill names ranked by total unique job count."""
    exploded = jobs.explode("required_skills")
    return (
        exploded.groupby("required_skills")["job_id"]
        .nunique()
        .nlargest(top_n)
        .index.tolist()
    )


def forecast_table(
    jobs: pd.DataFrame,
    top_n: int = 12,
    horizons: list[int] | None = None,
) -> pd.DataFrame:
    """Forecast demand for the top-N skills and return a summary table.

    Each row represents one skill × one horizon combination.
    """
    if horizons is None:
        horizons = [3, 6, 12]
    skills = top_skills_by_demand(jobs, top_n)
    parts: list[pd.DataFrame] = []
    for skill in skills:
        series = _monthly_series(jobs, skill)
        df = forecast_skill(series, horizons)
        if df.empty:
            continue
        df.insert(0, "skill", skill)
        df["current_demand"] = int(series.iloc[-1]) if len(series) else 0
        df["avg_monthly_demand"] = round(float(series.mean()), 1) if len(series) else 0.0
        parts.append(df)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def chart_data(jobs: pd.DataFrame, top_n: int = 8, forecast_months: int = 6) -> pd.DataFrame:
    """Return historical + forecast combined DataFrame ready for a line chart.

    Columns: skill, period (str), demand (float), series_type ('Historical'|'Forecast').
    """
    skills = top_skills_by_demand(jobs, top_n)
    records: list[dict] = []
    for skill in skills:
        series = _monthly_series(jobs, skill)
        if len(series) < 3:
            continue
        for period, count in series.items():
            records.append(
                {"skill": skill, "period": str(period), "demand": float(count), "series_type": "Historical"}
            )
        x = np.arange(len(series), dtype=float).reshape(-1, 1)
        y = series.values.astype(float)
        model = LinearRegression().fit(x, y)
        last = series.index[-1]
        for h in range(1, forecast_months + 1):
            predicted = max(0.0, float(model.predict([[len(series) + h - 1]])[0]))
            records.append(
                {"skill": skill, "period": str(last + h), "demand": round(predicted, 1), "series_type": "Forecast"}
            )
    return pd.DataFrame(records)


def growth_ranking(jobs: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Rank skills by their linear trend slope (demand acceleration).

    Returns a DataFrame with skill, slope, current_demand, and growth_label.
    """
    skills = top_skills_by_demand(jobs, top_n)
    rows: list[dict] = []
    for skill in skills:
        series = _monthly_series(jobs, skill)
        if len(series) < 3:
            continue
        x = np.arange(len(series), dtype=float).reshape(-1, 1)
        y = series.values.astype(float)
        model = LinearRegression().fit(x, y)
        slope = float(model.coef_[0])
        rows.append(
            {
                "skill": skill,
                "monthly_growth": round(slope, 3),
                "current_demand": int(series.iloc[-1]),
                "growth_label": _label(slope),
            }
        )
    return pd.DataFrame(rows).sort_values("monthly_growth", ascending=False).reset_index(drop=True)


def _label(slope: float) -> str:
    if slope > 1.5:
        return "Rocket"
    if slope > 0.5:
        return "Rising"
    if slope > 0:
        return "Stable"
    return "Declining"
