"""Plotly chart builders used by the dashboard."""

from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ACCENT = "#00ff9d"
TEMPLATE = "plotly_dark"


def gap_bar(gap: pd.DataFrame, limit: int = 20) -> go.Figure:
    frame = gap.head(limit).sort_values("gap_score")
    fig = px.bar(frame, x="gap_score", y="skill", color="gap_category", orientation="h", template=TEMPLATE)
    fig.update_layout(height=640, margin=dict(l=10, r=10, t=40, b=10), title="Highest Skill Gaps")
    return fig


def demand_supply_scatter(gap: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        gap,
        x="supply_count",
        y="demand_count",
        size="market_pressure",
        color="gap_category",
        hover_name="skill",
        template=TEMPLATE,
        title="Supply vs Demand Pressure",
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=max(gap["supply_count"].max(), 1), y1=max(gap["supply_count"].max(), 1), line=dict(color=ACCENT, dash="dash"))
    return fig


def heatmap(location_gap: pd.DataFrame, top_skills: list[str]) -> go.Figure:
    frame = location_gap[location_gap["skill"].isin(top_skills)]
    pivot = frame.pivot_table(index="location", columns="skill", values="gap_score", aggfunc="mean").fillna(0)
    fig = px.imshow(pivot, color_continuous_scale="Viridis", template=TEMPLATE, title="Location Skill Gap Heatmap")
    fig.update_layout(height=620)
    return fig


def trend_line(jobs: pd.DataFrame) -> go.Figure:
    frame = jobs.copy()
    frame["month"] = pd.to_datetime(frame["posted_at"], errors="coerce").dt.to_period("M").astype(str)
    trend = frame.explode("required_skills").groupby(["month", "required_skills"], as_index=False)["job_id"].nunique()
    top = trend.groupby("required_skills")["job_id"].sum().nlargest(8).index
    trend = trend[trend["required_skills"].isin(top)]
    return px.line(trend, x="month", y="job_id", color="required_skills", template=TEMPLATE, title="Demand Trend By Skill")


def role_bar(jobs: pd.DataFrame) -> go.Figure:
    frame = jobs.groupby("title", as_index=False)["job_id"].nunique().sort_values("job_id", ascending=False)
    return px.bar(frame, x="title", y="job_id", template=TEMPLATE, color_discrete_sequence=[ACCENT], title="Open Demand By Role")


def word_cloud_figure(freq: pd.DataFrame, freq_col: str = "demand_count") -> go.Figure | None:
    """Render a skill word cloud as a Plotly figure embedding a PNG image.

    Returns None if the wordcloud package is unavailable.
    """
    try:
        from wordcloud import WordCloud
    except ImportError:
        return None

    weights = dict(zip(freq["skill"].tolist(), freq[freq_col].tolist()))
    wc = WordCloud(
        width=900,
        height=420,
        background_color="#07100d",
        colormap="cool",
        max_words=60,
    ).generate_from_frequencies(weights)
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    buf.seek(0)
    import base64

    encoded = base64.b64encode(buf.read()).decode()
    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{encoded}",
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            sizex=1,
            sizey=1,
            sizing="stretch",
            layer="below",
        )
    )
    fig.update_layout(
        template=TEMPLATE,
        title="Skill Demand Word Cloud",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=420,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def salary_box(jobs: pd.DataFrame) -> go.Figure:
    """Box-plot of offered salary ranges grouped by job role."""
    frame = jobs[["title", "salary_min_lpa", "salary_max_lpa"]].copy()
    frame["salary_mid_lpa"] = (frame["salary_min_lpa"] + frame["salary_max_lpa"]) / 2
    fig = px.box(
        frame,
        x="title",
        y="salary_mid_lpa",
        color="title",
        template=TEMPLATE,
        title="Salary Ranges by Role (Midpoint, LPA)",
        labels={"salary_mid_lpa": "Midpoint Salary (LPA)", "title": "Role"},
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-30, height=480)
    return fig


def forecast_chart(chart_df: pd.DataFrame) -> go.Figure:
    """Line chart showing historical demand + dashed forecast per skill."""
    if chart_df.empty:
        return go.Figure()
    fig = go.Figure()
    skills = chart_df["skill"].unique()
    colors = px.colors.qualitative.Vivid
    for i, skill in enumerate(skills):
        color = colors[i % len(colors)]
        hist = chart_df[(chart_df["skill"] == skill) & (chart_df["series_type"] == "Historical")]
        fcast = chart_df[(chart_df["skill"] == skill) & (chart_df["series_type"] == "Forecast")]
        fig.add_trace(
            go.Scatter(
                x=hist["period"],
                y=hist["demand"],
                mode="lines",
                name=skill,
                line=dict(color=color, width=2),
                legendgroup=skill,
            )
        )
        if not fcast.empty:
            fig.add_trace(
                go.Scatter(
                    x=fcast["period"],
                    y=fcast["demand"],
                    mode="lines",
                    name=f"{skill} (forecast)",
                    line=dict(color=color, width=2, dash="dot"),
                    legendgroup=skill,
                    showlegend=False,
                )
            )
    fig.update_layout(
        template=TEMPLATE,
        title="Skill Demand Forecast (solid = historical, dotted = forecast)",
        xaxis_title="Month",
        yaxis_title="Unique Job Postings",
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def growth_bar(growth_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of skill growth velocity (slope)."""
    frame = growth_df.sort_values("monthly_growth")
    color_map = {"Rocket": "#00ff9d", "Rising": "#00b4d8", "Stable": "#f4a261", "Declining": "#e63946"}
    colors = [color_map.get(label, ACCENT) for label in frame["growth_label"]]
    fig = go.Figure(
        go.Bar(
            x=frame["monthly_growth"],
            y=frame["skill"],
            orientation="h",
            marker_color=colors,
            text=frame["growth_label"],
            textposition="outside",
        )
    )
    fig.update_layout(
        template=TEMPLATE,
        title="Skill Demand Velocity (monthly posting growth rate)",
        xaxis_title="Monthly Growth (job postings / month)",
        height=500,
        margin=dict(l=10, r=80, t=50, b=10),
    )
    return fig


def radar_chart(candidate_skills: list[str], gap: pd.DataFrame) -> go.Figure:
    """Radar chart comparing candidate's skill coverage vs. market demand by category.

    Angles represent skill taxonomy categories. Each axis = % of category skills
    that are in high demand, with the candidate's coverage overlaid.
    """
    from src.data_generator import SKILL_TAXONOMY

    categories = list(SKILL_TAXONOMY.keys())
    candidate_set = set(candidate_skills)
    demand_set = set(gap[gap["gap_score"] > 0.1]["skill"].tolist())

    market_vals, candidate_vals = [], []
    for cat in categories:
        cat_skills = set(SKILL_TAXONOMY[cat])
        in_demand = cat_skills & demand_set
        covered = cat_skills & candidate_set
        market_vals.append(len(in_demand) / max(len(cat_skills), 1))
        candidate_vals.append(len(covered) / max(len(cat_skills), 1))

    # Close the polygon
    categories_c = categories + [categories[0]]
    market_c = market_vals + [market_vals[0]]
    candidate_c = candidate_vals + [candidate_vals[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=market_c,
            theta=categories_c,
            fill="toself",
            name="Market Demand",
            line_color=ACCENT,
            fillcolor="rgba(0,255,157,0.15)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=candidate_c,
            theta=categories_c,
            fill="toself",
            name="Your Skills",
            line_color="#00b4d8",
            fillcolor="rgba(0,180,216,0.20)",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickformat=".0%")),
        template=TEMPLATE,
        title="Your Skill Coverage vs. Market Demand",
        height=480,
        showlegend=True,
    )
    return fig


def sankey_skill_channel(recommendations: pd.DataFrame) -> go.Figure:
    labels = list(recommendations["skill"].head(8))
    channels = sorted({channel.strip() for value in recommendations["target_channels"].head(8) for channel in value.split(",")})
    all_labels = labels + channels
    source, target, value = [], [], []
    for _, row in recommendations.head(8).iterrows():
        for channel in [part.strip() for part in row["target_channels"].split(",")[:3]]:
            source.append(all_labels.index(row["skill"]))
            target.append(all_labels.index(channel))
            value.append(1)
    fig = go.Figure(data=[go.Sankey(node=dict(label=all_labels, color=ACCENT), link=dict(source=source, target=target, value=value))])
    fig.update_layout(template=TEMPLATE, title="Skill To Sourcing Channel Map", height=520)
    return fig
