#!/usr/bin/env bash
set -euo pipefail

python -m pip install -r requirements.txt
python scripts/generate_synthetic_data.py --resumes 15000 --jobs 8000
python main_pipeline.py
streamlit run app/main.py
