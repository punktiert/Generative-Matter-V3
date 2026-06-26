-- DuckDB queries over Generative Matter V3.
-- Run from the repository root, e.g.:
--   duckdb -c ".read examples/queries.sql"
-- or paste individual statements into a DuckDB session. No import step needed —
-- DuckDB reads the Parquet/CSV files directly. Join key is `id` (== `formula`).

-- 1) Top architectural candidates by composite score, with firing window + cost
SELECT a.formula,
       a.categories,
       s.score_composite,
       s.corrected_temp_min_c,
       s.corrected_temp_max_c,
       r.estimated_cost_eur,
       r.confidence
FROM 'data/architectural_candidates.parquet' a
JOIN 'data/scores.parquet'  s USING (id)
LEFT JOIN 'data/recipes.parquet' r USING (id)
ORDER BY s.score_composite DESC
LIMIT 30;

-- 2) Everything fireable below 900 C (phase-corrected upper bound)
SELECT formula, corrected_temp_max_c, score_composite
FROM 'data/scores.parquet'
WHERE corrected_temp_max_c < 900
ORDER BY score_composite DESC
LIMIT 50;

-- 3) Semiconductors with a high structural score
SELECT m.formula, m.bandgap_ev, s.score_structural
FROM 'data/materials.parquet' m
JOIN 'data/scores.parquet'    s USING (id)
WHERE m.bandgap_type = 'semiconductor' AND s.score_structural >= 8
ORDER BY s.score_structural DESC
LIMIT 25;

-- 4) Trace one published book material down to its recipe
SELECT *
FROM 'data/atlas_published.csv'
WHERE formula = 'Er4FeMnSi4';
