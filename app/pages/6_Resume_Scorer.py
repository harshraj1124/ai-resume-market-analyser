"""Resume Market-Fit Scorer: paste a resume and get an instant market intelligence report."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from app.ui import inject_theme, load_data
from src.gap_analysis import compute_gap_table
from src.skill_extractor import SkillExtractor, load_taxonomy
from src.visualization import radar_chart

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "data" / "synthetic" / "skills_taxonomy.json"

SAMPLE_RESUME = """\
Priya Nair | Senior Software Engineer | Bangalore
8 years of experience building scalable backend systems and data pipelines.

Skills: Python, FastAPI, SQL, PostgreSQL, Docker, Kubernetes, AWS, Apache Spark, Airflow,
scikit-learn, Tableau, Git, Linux, Microservices, Kafka.

Recent work includes deploying ML models to production (MLOps), designing REST APIs,
and building ETL pipelines on Databricks. Interested in GenAI and LLM integrations.
"""

st.set_page_config(page_title="Resume Scorer", layout="wide")
inject_theme()

resumes, jobs, _, _, _ = load_data()
gap = compute_gap_table(resumes, jobs)


@st.cache_resource(show_spinner=False)
def _extractor() -> SkillExtractor:
    if TAXONOMY_PATH.exists():
        taxonomy = load_taxonomy(TAXONOMY_PATH)
    else:
        from src.data_generator import SKILL_TAXONOMY

        taxonomy = SKILL_TAXONOMY
    return SkillExtractor(taxonomy, use_spacy=False)


extractor = _extractor()

st.title("Resume Market-Fit Scorer")
st.caption(
    "Paste any resume text below. The system extracts your skills and scores them "
    "against live market demand to identify gaps, strengths, and upskilling priorities."
)

col_input, col_info = st.columns([1.6, 1])

with col_input:
    resume_text = st.text_area(
        "Paste resume text here",
        value=SAMPLE_RESUME,
        height=280,
        help="Plain text works best. PDF content can be pasted after copying from a PDF reader.",
    )
    analyze = st.button("Analyze Resume", type="primary", use_container_width=True)

with col_info:
    st.markdown(
        """
        **How it works**
        1. Skill extraction via taxonomy regex + alias resolution
        2. Each skill is matched to the live supply-demand gap table
        3. Market-fit score = weighted coverage of high-demand skills
        4. Radar chart shows your category coverage vs. market shape
        5. Upskilling picks are the highest-gap skills adjacent to your profile
        """
    )
    st.info("No data leaves your browser. Analysis runs entirely on local data.")

if not analyze:
    st.stop()

with st.spinner("Extracting skills..."):
    detected = extractor.extract(resume_text)

if not detected:
    st.warning("No recognizable skills found. Try adding more technical terms.")
    st.stop()

detected_set = set(detected)
gap_indexed = gap.set_index("skill")

critical_skills = set(gap[gap["gap_score"] > 0.6]["skill"])
high_demand_skills = set(gap[gap["gap_score"] > 0.3]["skill"])
all_positive_gap = set(gap[gap["gap_score"] > 0]["skill"])

matched_critical = detected_set & critical_skills
matched_high = detected_set & high_demand_skills
matched_positive = detected_set & all_positive_gap

coverage_score = (
    len(matched_critical) * 3
    + len(matched_high - matched_critical) * 2
    + len(matched_positive - matched_high)
) / max(
    len(critical_skills) * 3
    + len(high_demand_skills - critical_skills) * 2
    + len(all_positive_gap - high_demand_skills),
    1,
)
market_fit_pct = min(100, round(coverage_score * 100))

missing_critical = critical_skills - detected_set
missing_high = (high_demand_skills - critical_skills) - detected_set

st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Skills Detected", len(detected))
m2.metric("Market-Fit Score", f"{market_fit_pct}%")
m3.metric("Critical Gaps Covered", f"{len(matched_critical)} / {len(critical_skills)}")
m4.metric("High-Demand Gaps Covered", f"{len(matched_high)} / {len(high_demand_skills)}")

if market_fit_pct >= 70:
    badge, badge_color = "STRONG FIT", "#00ff9d"
    message = "Your skill profile aligns well with current market demand. Focus on topping up critical shortage areas."
elif market_fit_pct >= 40:
    badge, badge_color = "MODERATE FIT", "#f4a261"
    message = "You cover key fundamentals. Targeted upskilling in 2-3 critical areas will significantly improve demand."
else:
    badge, badge_color = "NEEDS DEVELOPMENT", "#e63946"
    message = "Consider a focused learning sprint on the top 3 upskilling recommendations below."

st.markdown(
    f"""
    <div style="border:2px solid {badge_color}; border-radius:12px; padding:1rem 1.5rem;
                background:rgba(0,0,0,0.3); margin:1rem 0;">
        <span style="color:{badge_color}; font-size:1.4rem; font-weight:700;">{badge}</span>
        &nbsp;&nbsp;<span style="opacity:0.85;">{message}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.1, 1])

with left:
    st.plotly_chart(radar_chart(detected, gap), use_container_width=True)

with right:
    st.subheader("Detected Skills")
    skill_rows = []
    for skill in sorted(detected):
        if skill in gap_indexed.index:
            row = gap_indexed.loc[skill]
            skill_rows.append(
                {
                    "Skill": skill,
                    "Category": extractor.categorize(skill),
                    "Gap Score": round(float(row["gap_score"]), 3),
                    "Market Status": row["gap_category"],
                    "Demand": int(row["demand_count"]),
                    "Supply": int(row["supply_count"]),
                }
            )
        else:
            skill_rows.append(
                {
                    "Skill": skill,
                    "Category": extractor.categorize(skill),
                    "Gap Score": 0.0,
                    "Market Status": "Not in market index",
                    "Demand": 0,
                    "Supply": 0,
                }
            )
    skill_df = pd.DataFrame(skill_rows).sort_values("Gap Score", ascending=False)
    st.dataframe(skill_df, use_container_width=True, hide_index=True, height=380)

st.divider()
st.subheader("Upskilling Recommendations")
st.caption("High-gap skills closest to your current profile, ranked by urgency.")

candidate_categories = {extractor.categorize(s) for s in detected}

upskillers = []
for skill in sorted(missing_critical | missing_high):
    if skill not in gap_indexed.index:
        continue
    r = gap_indexed.loc[skill]
    adj = extractor.categorize(skill) in candidate_categories
    upskillers.append(
        {
            "skill": skill,
            "gap_score": float(r["gap_score"]),
            "gap_category": r["gap_category"],
            "adjacent": adj,
            "demand": int(r["demand_count"]),
        }
    )

upskillers.sort(key=lambda x: (x["adjacent"], x["gap_score"]), reverse=True)

if upskillers:
    for i, rec in enumerate(upskillers[:6], 1):
        with st.container(border=True):
            c1, c2, c3 = st.columns([0.3, 0.4, 0.3])
            c1.markdown(f"**#{i} - {rec['skill']}**")
            c1.caption(rec["gap_category"])
            c2.write(
                f"Gap score: **{rec['gap_score']:.3f}** &nbsp;|&nbsp; "
                f"{'Adjacent to your skills' if rec['adjacent'] else 'New category - high reward'}",
                unsafe_allow_html=True,
            )
            c2.write(f"Market demand: **{rec['demand']}** open roles requiring this skill.")
            c3.progress(min(1.0, rec["gap_score"]), text="Shortage severity")
else:
    st.success("You already cover all critical and high-demand skills. Consider deepening existing expertise.")

st.divider()
report = {
    "market_fit_score": market_fit_pct,
    "badge": badge,
    "detected_skills": sorted(detected),
    "critical_gaps_covered": sorted(matched_critical),
    "missing_critical_skills": sorted(missing_critical),
    "missing_high_demand_skills": sorted(missing_high),
    "upskilling_recommendations": [u["skill"] for u in upskillers[:6]],
}
st.download_button(
    "Export Score Report (JSON)",
    data=json.dumps(report, indent=2),
    file_name="resume_market_fit_report.json",
    mime="application/json",
)
