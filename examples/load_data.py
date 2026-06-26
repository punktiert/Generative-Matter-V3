"""Minimal loaders + a join example for Generative Matter V3.

Run from the repository root:

    python examples/load_data.py

Uses only the standard library for the JSONL/CSV paths; DuckDB (optional) for SQL.
"""
import csv
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def stream(layer: str):
    """Yield full (nested) records from a layer's JSONL.gz — no third-party deps."""
    with gzip.open(DATA / f"{layer}.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def main() -> None:
    # 1) HIGH-confidence, low-cost recipes that actually have a firing template
    n = 0
    for r in stream("recipes"):
        fs = r.get("firing_schedule") or {}
        cost = r.get("estimated_cost_eur")
        if r.get("confidence") == "HIGH" and fs.get("peak_c") and cost is not None and cost < 50:
            n += 1
    print(f"HIGH-confidence recipes under EUR 50 with a firing template: {n}")

    # 2) the materials that made it into the printed books (CSV layer)
    with open(DATA / "atlas_published.csv", encoding="utf-8") as fh:
        book = [row for row in csv.DictReader(fh) if row["in_printed_book"] == "true"]
    print(f"materials in the printed books: {len(book)}")
    print("first three:", [b["formula"] for b in book[:3]])

    # 3) optional: SQL over the Parquet layers with DuckDB
    try:
        import duckdb
    except ImportError:
        print("(pip install duckdb to run the SQL example)")
        return
    rows = duckdb.sql(
        "SELECT m.formula, s.score_composite "
        "FROM 'data/materials.parquet' m "
        "JOIN 'data/scores.parquet' s USING (id) "
        "ORDER BY s.score_composite DESC LIMIT 5"
    ).fetchall()
    print("top composite scores:", rows)


if __name__ == "__main__":
    main()
