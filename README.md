# Generative Matter V3

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-pending-blue.svg)](#citation)
[![Data: JSONL + Parquet](https://img.shields.io/badge/data-JSONL%20%2B%20Parquet-brightgreen.svg)](data/)

An open dataset of **AI-generated synthetic materials for architecture**.

Roughly **120,000 candidate compositions** derived from Google DeepMind's
[GNoME](https://github.com/google-deepmind/materials_discovery) stable-materials
corpus — each carrying a workshop recipe, scored and filtered for architectural use,
and narrowed down to the **245 materials published in the *Synthetic Types Atlas*** (2026).

This is the data behind the book. It is intended to be read by **researchers and by AI
agents** with minimal ceremony: flat files, one stable join key, a documented schema,
and an honest account of what the numbers do and do not mean.

> **V3** is the curated successor to the earlier `Generative-Matter-V2` filter (2025,
> GPT-4o-mini). About 15 % of that early repository's recipes carried mismatched or
> implausible ingredients; V3 is the re-scored, re-filtered, and re-written database.

---

## What's inside

The dataset is **layered**: each layer is one stage of the pipeline, in its own file,
joined to the others by the `id` column (e.g. `"Cs1S6Zr3"` — identical to `formula`).

| # | Layer | Rows | What it is | Files |
|---|-------|-----:|-----------|-------|
| 1 | **materials** | 119,987 | The full pool — composition + DFT/structural properties ("what it is") | `materials.jsonl.gz` · `.parquet` |
| 2 | **recipes** | 106,406 | Workshop recipes — ingredients (precursor, mass, safety), firing schedule, cost, confidence ("how to make it") | `recipes.jsonl.gz` · `.parquet` |
| 3 | **scores** | 103,588 | Sustainability / structural / sensory / novelty / composite scores + architectural categories + corrected firing ranges | `scores.jsonl.gz` · `.parquet` |
| 4 | **architectural_candidates** | 15,984 | The architectural short-list — tiered, safety-screened, categorized | `architectural_candidates.jsonl.gz` · `.parquet` |
| 5 | **atlas_published** | 253 (245 in the printed books) | The selection that became the *Synthetic Types Atlas*, with physical units and firing corrections | `atlas_published.csv` |

`data/samples/` holds the first 200 rows of each big layer as CSV, so you can browse
the shape directly on GitHub without downloading anything.

**Pipeline / provenance:**

```
GNoME (Google DeepMind, ~380k stable crystals)
   └─▶ materials (119,987)            composition + DFT properties
         ├─▶ recipes (106,406)        AI-drafted synthesis recipes
         ├─▶ scores (103,588)         scored + categorized for architecture
               └─▶ architectural_candidates (15,984)   filtered short-list
                     └─▶ atlas_published (245)          published in the books
```

---

## Quick start

Every layer is shipped two ways: **`.jsonl.gz`** (universal, streamable, full nesting —
best for agents and shell tools) and **`.parquet`** (columnar, fast — best for analytics).
Pick whichever your stack likes.

**Python (pandas + pyarrow):**

```python
import pandas as pd

materials = pd.read_parquet("data/materials.parquet")
recipes   = pd.read_parquet("data/recipes.parquet")          # nested fields are JSON strings
atlas     = pd.read_csv("data/atlas_published.csv")

# everything that made it into the printed book, with its workshop recipe
published = atlas[atlas.in_printed_book == "true"]
print(published[["formula", "architectural_role", "firing_peak_c", "estimated_cost_eur"]].head())

df = published.merge(recipes[["formula", "ingredients", "confidence"]], on="formula", how="left")
```

**Stream the JSONL with no dependencies (great for agents):**

```python
import gzip, json
with gzip.open("data/recipes.jsonl.gz", "rt", encoding="utf-8") as fh:
    for line in fh:
        r = json.loads(line)
        if r["confidence"] == "HIGH" and r["estimated_cost_eur"] and r["estimated_cost_eur"] < 50:
            print(r["formula"], r["firing_schedule"].get("peak_c"))
```

**SQL (DuckDB, no import step):**

```sql
SELECT m.formula, m.bandgap_ev, s.score_composite
FROM 'data/materials.parquet' m
JOIN 'data/scores.parquet'    s USING (id)
WHERE s.score_composite > 8
ORDER BY s.score_composite DESC
LIMIT 20;
```

More in [`examples/`](examples/). AI agents: start with **[AGENTS.md](AGENTS.md)**.

---

## Schema

Full per-column data dictionary, types, and units in **[SCHEMA.md](SCHEMA.md)**.

In Parquet and the CSV samples, nested fields (ingredient lists, firing schedules,
category lists) are stored as **JSON strings** — `json.loads()` them. In the
`.jsonl.gz` files they keep their native nested structure.

---

## Honest caveats — read before you synthesise anything

This dataset is a set of **machine-generated hypotheses**, not a validated handbook.

- **Stability ≠ synthesizability.** GNoME predicts that a structure is thermodynamically
  stable at 0 K — not how to make it, at what temperature, in what atmosphere, or whether
  the fired body holds together. Synthesizability is an open research problem.
- **Recipes are AI-drafted.** Ingredients, masses, and procedures are generated, not
  laboratory-verified. Treat every recipe as an experiment to be designed, not a protocol
  to be followed.
- **Firing temperatures are best-estimates.** The source database reports where a body
  first softens or loses carbonates; the temperature at which the chemistry actually reacts
  through is often 200–700 °C higher. The `atlas_published` set carries phase-corrected
  values; the raw layers do not. Validate on the first firing.
- **Some raw DFT fields are in the source's internal units.** `volume` and `density` in the
  `materials` layer are raw database values and are **not** normalized to SI (they are not
  physical g/cm³ / Å³). Physical, corrected values for the curated set live in
  `atlas_published.csv` (`density_g_cm3`, `firing_peak_c`, …).
- **Safety flags are guidance, not an SDS.** They are AI-generated. Always consult the
  manufacturer's safety data sheet and a qualified person before handling any precursor.

---

## The books

The curated end of this dataset is published as a two-volume atlas, written, researched,
designed, and visualised by AI agents and directed by **Prof. Dr. Daniel Koehler**:

- ***Synthetic Types Atlas — Volume I: Research Papers*** (the theory + 36 illustrated material studies)
- ***Synthetic Types Atlas — Volume II: The Recipe Atlas*** (245 one-page recipes)

State Academy of Art and Design Stuttgart (Staatliche Akademie der Bildenden Künste
Stuttgart), Studio *Synthetische Typen / Modelling Models*, Summer 2026.

---

## Relation to previous versions

This dataset supersedes **[Generative-Matter-V2](https://github.com/catgraubard/Generative-Matter-V2)**
(Graubard, 2025), the first open architectural filtering of the GNoME database. V3 is
independently regenerated from the project's own pipeline — re-scored, re-filtered, and
re-written — and shares only the upstream GNoME source with V2, not its files. About 15 % of
the early V2 recipes carried mismatched or implausible ingredients; those are corrected here.

## Citation

If you use this dataset, please cite it (see [`CITATION.cff`](CITATION.cff)). A DOI will be
minted via Zenodo on first release; the badge above and the citation file will be updated
with the real identifier at that point.

```
Koehler, D. (2026). Generative Matter V3: An open dataset of AI-generated
synthetic materials for architecture [Data set]. DOI: <pending>.
```

This work builds directly on:

- Merchant, A. et al. (2023). *Scaling deep learning for materials discovery.* Nature 624. (GNoME)
- Graubard, C. & Koehler, D. (2025). *Generative Matter for Architecture: LLM-Guided Discovery
  and Low-Tech Prototyping of Resilient Synthetic Materials.* ACADIA 2025 (Vanguard Paper Award).

---

## License

**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).**
You may share and adapt the data for **non-commercial** purposes, with **attribution**.
See [`LICENSE`](LICENSE) for the full legal code, and [SCHEMA.md](SCHEMA.md) for how to
attribute. For commercial licensing, contact the author.

---

## Credits

Conceived and directed by **Daniel Koehler**. The pipeline was run by AI systems:

- **GNoME** (Google DeepMind) — discovery of the underlying stable crystal structures.
- **GPT-4o / GPT-4o-mini** (OpenAI) — the first architectural filtering and synthesis-recipe drafting.
- **Claude** (Anthropic, Opus 4.8 + Sonnet, via Claude Code) — re-scoring, architectural
  filtering, recipe rewriting, and the assembly of this dataset.

The project began in 2023 in the *Architecture Computation* seminar; **Catherine Graubard**
deepened it in her master's thesis and co-authored the founding ACADIA paper. With thanks to
the GNoME team at Google DeepMind for releasing the corpus on which all of this stands.
