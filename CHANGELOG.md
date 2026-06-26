# Changelog

## 1.0.0 — 2026-06-26

Initial public release.

- **Layers:** `materials` (119,987), `recipes` (106,406), `scores` (103,588),
  `architectural_candidates` (15,984), `atlas_published` (253; 245 in the printed books).
- **Formats:** `.jsonl.gz` (full nesting) + `.parquet` (columnar) for each big layer;
  `.csv` samples (first 200 rows) for browsing; `atlas_published` as CSV.
- **Docs:** `README`, `SCHEMA`, `AGENTS.md`, `CITATION.cff`, `.zenodo.json`, examples.
- **License:** CC BY-NC 4.0 (non-commercial, with attribution).

Supersedes the 2025 **Generative-Matter-V2** architectural filter (GPT-4o-mini). About 15 %
of that early repository's recipes carried mismatched or implausible ingredients; V3 is the
re-scored, re-filtered, and re-written database, with phase-corrected firing for the curated
atlas set.
