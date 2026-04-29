# AI Resume Sourcing & Labor Market Demand Analyzer

A production-ready analytics system for recruitment teams that compares resume supply against job-market demand, highlights skill shortages, and generates sourcing recommendations with India-first market context.

## Highlights

- Parses resume-like candidate records and demand-side job postings.
- Generates 15,000 synthetic resumes and 8,000 synthetic job postings by default.
- Models Indian hiring hubs including Bangalore, Hyderabad, Pune, Chennai, Delhi NCR, Mumbai, Gurugram, Noida, and Kochi.
- Extracts and normalizes skills with a taxonomy-driven NLP pipeline.
- Computes supply-demand gap scores with the requested formula.
- Ships a multi-page Streamlit dashboard with Plotly visuals, filters, exports, and recommendations.

## Screenshots

Place screenshots here after running locally:

- `docs/screenshots/overview.png`
- `docs/screenshots/skill-trends.png`
- `docs/screenshots/gap-analysis.png`
- `docs/screenshots/recommendations.png`

## Quick Start

```bash
cd ai-resume-market-analyzer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_lg
python scripts/generate_synthetic_data.py --resumes 15000 --jobs 8000
python main_pipeline.py
streamlit run app/main.py
```

On Windows PowerShell:

```powershell
cd ai-resume-market-analyzer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_lg
python scripts\generate_synthetic_data.py --resumes 15000 --jobs 8000
python main_pipeline.py
streamlit run app\main.py
```

For a smaller demo:

```bash
python scripts/generate_synthetic_data.py --resumes 1000 --jobs 500
python main_pipeline.py
streamlit run app/main.py
```

## Project Structure

```text
ai-resume-market-analyzer/
  app/                    Streamlit app and pages
  data/                   Raw, processed, and synthetic datasets
  docs/                   Market research and project notes
  notebooks/              EDA notebook
  scripts/                Data generation scripts
  src/                    Analysis modules
  tests/                  Pipeline tests
  main_pipeline.py        One-command analysis pipeline
```

## Gap Score

```python
gap_score = (demand_count - supply_count) / (demand_count + 1)
```

Categories:

- `CRITICAL SHORTAGE FIRE`: score greater than `0.6`
- `HIGH DEMAND`: score greater than `0.3`
- `BALANCED`: score between `-0.2` and `0.3`
- `SUPPLY SURPLUS`: score less than or equal to `-0.2`

## How To Use

1. Generate synthetic data.
2. Run `main_pipeline.py` to transform data and produce analytics tables.
3. Launch Streamlit.
4. Use sidebar filters for location, industry, experience, and date range.
5. Export filtered tables from each page for recruiting campaigns.

## Future Enhancements

- Add compliant live scraping connectors for Naukri, LinkedIn India, Indeed India, and company career pages.
- Add vector embeddings for resume-job semantic matching.
- Add ATS integrations for Greenhouse, Lever, Workday, and Darwinbox.
- Add salary intelligence by skill, city, and seniority.
- Add candidate outreach sequence generation with approval workflows.
