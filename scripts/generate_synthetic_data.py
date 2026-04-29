"""CLI for generating synthetic resume and labor-market data."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_generator import GeneratorConfig, generate_all


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic resume and job-posting data.")
    parser.add_argument("--resumes", type=int, default=15_000, help="Number of resume records to generate.")
    parser.add_argument("--jobs", type=int, default=8_000, help="Number of job postings to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "synthetic")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    config = GeneratorConfig(resumes=args.resumes, jobs=args.jobs, seed=args.seed, output_dir=args.output_dir)
    paths = generate_all(config)
    for name, path in paths.items():
        logging.info("%s written to %s", name, path)


if __name__ == "__main__":
    main()
