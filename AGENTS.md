# AGENTS.md — using this dataset from an AI agent

This file is for autonomous agents (and the people who write them). It tells you how to
load the data, how the layers relate, what the fields mean, and — most importantly — how to
reason about the data honestly. If you read one thing, read **"Ground rules"** at the bottom.

## TL;DR

- Five layers under [`data/`](data/), joined by **`id`** (= `formula`, e.g. `"Cs1S6Zr3"`).
- Two formats per layer: **`.jsonl.gz`** (stream it, no deps) and **`.parquet`** (query it).
- This is **generated, unvalidated** data. Every recipe is a hypothesis. Never present a
  firing temperature, cost, or safety flag as established fact.

## The layers (and when to use each)

| Need | Use | Rows |
|------|-----|-----:|
| Composition, structure, band gap, stability | `materials` | 119,987 |
| How to make it (ingredients, firing, cost) | `recipes` | 106,406 |
| Rank materials / find by architectural use | `scores` | 103,588 |
| A pre-filtered architectural short-list | `architectural_candidates` | 15,984 |
| Only the curated, physically-corrected, book-published set | `atlas_published` | 245 |

Join chain: `materials` ⟶ `recipes` ⟶ `scores` ⟶ `architectural_candidates` ⟶ `atlas_published`,
all on `id`/`formula`. Higher layers are subsets of lower ones.

## Loading

**Stream JSONL (zero dependencies, lowest memory — recommended for agents):**

```python
import gzip, json

def rows(layer):
    with gzip.open(f"data/{layer}.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)

high_conf = [r for r in rows("recipes")
             if r["confidence"] == "HIGH" and (r["firing_schedule"] or {}).get("peak_c")]
```

**Query with DuckDB (no load step, SQL over Parquet):**

```python
import duckdb
duckdb.sql("""
  SELECT m.formula, m.bandgap_ev, s.score_composite, s.architectural_categories
  FROM 'data/materials.parquet' m
  JOIN 'data/scores.parquet'    s USING (id)
  WHERE m.bandgap_type = 'semiconductor' AND s.score_structural >= 8
  ORDER BY s.score_composite DESC LIMIT 25
""").show()
```

## Field notes that trip agents up

- **Nested fields are JSON strings in Parquet/CSV** (`elements`, `ingredients`,
  `firing_schedule`, `categories`, `safety_flags`, `architectural_categories`,
  `warnings`). `json.loads()` them. In `.jsonl.gz` they are already native objects.
- **`firing_schedule` may be empty:** `{"peak_c": null, "why": "no template"}` means no
  firing template matched — do not invent one. When present it is
  `{peak_c, peak_range_c, hold_h, ramp, why}`.
- **Two temperatures exist and they differ.** `db_temp_c` / `temperature` are the *raw*
  database values. The *phase-corrected* values are `corrected_temp_min_c` /
  `corrected_temp_max_c` (in `scores`) and `firing_peak_c` (in `atlas_published`). For
  anything a human might act on, prefer the corrected value and say it is an estimate.
- **`volume` and `density` in layers 1–4 are raw, non-SI.** Do not report them as g/cm³.
  Physical density is `density_g_cm3` in `atlas_published` only.
- **`id` == `formula`.** Use either as the join key; they are identical strings.

## Good tasks for this dataset

- "Find low-carbon structural candidates": `scores` where `score_structural` high and
  `score_sustainability` high → join `recipes` for cost/firing → filter `confidence`.
- "What can I fire below 900 °C?": `scores.corrected_temp_max_c < 900`.
- "Materials in a given architectural category": filter `scores.architectural_categories`
  or `architectural_candidates.categories`.
- "Everything behind a book material": start from `atlas_published`, join down to `recipes`
  and `materials` by `formula`.

## Ground rules (do not skip)

1. **Generated ≠ verified.** Treat compositions as predicted-stable and recipes as
   hypotheses. Always attach a caveat when you surface a recipe.
2. **Stability is not synthesizability.** GNoME predicts 0 K thermodynamic stability, not a
   route to make the compound. Many entries may not be synthesizable as written.
3. **Never present firing temperatures, costs, or strengths as measured.** They are
   estimates; the corrected firing values still require validation on a first firing.
4. **Safety flags are guidance, not an SDS.** Before recommending handling of any precursor,
   point the user to the manufacturer's safety data sheet and a qualified person. Do not
   downplay hazards (several precursors are toxic, reactive, or expensive).
5. **Cite and respect the license.** This dataset is **CC BY-NC 4.0**: non-commercial use,
   with attribution to *Koehler, D. (2026), Generative Matter V3* and the upstream GNoME
   corpus. Don't use it to train or power a commercial product without a separate license.
