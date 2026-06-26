# Schema

Five layers, joined by **`id`** (a formula string such as `"Cs1S6Zr3"`; the `formula`
column is the same value). Every layer carries `id`/`formula` so any pair can be joined
directly.

**Formats.** Each big layer ships as `.jsonl.gz` (full nested structure) and `.parquet`
(columnar). In Parquet and in the CSV samples, **nested fields are JSON-encoded strings** —
`json.loads()` them. In `.jsonl.gz` they are native JSON.

**A note on units.** Layers 1–4 carry values **as provided by the source database**. Some
DFT/structural fields (`volume`, `density`) are in the source's internal scaling and are
**not** physical SI units — treat them as relative/identifier fields, not as g/cm³ or Å³.
Physically meaningful, phase-corrected values for the curated set are in
**`atlas_published.csv`** (layer 5).

---

## 1 · `materials` — composition + properties (119,987 rows)

The full candidate pool: what each material *is*.

| Column | Type | Description |
|--------|------|-------------|
| `id` | string | Stable identifier = formula, e.g. `Cs1S6Zr3`. Join key. |
| `formula` | string | Chemical formula (same as `id`). |
| `reduced_formula` | string | Reduced/normalised formula, e.g. `Cs(ZrS2)3`. |
| `elements` | list[string] | Constituent elements. *(JSON string in Parquet/CSV.)* |
| `n_elements` | int | Number of distinct elements. |
| `nsites` | int | Atoms in the unit cell. |
| `volume` | float | Unit-cell volume, **raw source units** (not Å³). |
| `density` | float | Density, **raw source units** (not g/cm³). |
| `crystal_system` | string | e.g. `monoclinic`, `cubic`. |
| `space_group` | string | Hermann–Mauguin symbol, e.g. `C2/m`. |
| `space_group_number` | int | 1–230. |
| `point_group` | string | e.g. `2/m`. |
| `dimensionality` | string | Structural motif, e.g. `intercalated ion`, `framework`. |
| `corrected_energy` | float | DFT total/corrected energy (source units). |
| `formation_energy_per_atom` | float | Formation energy per atom (source units). |
| `decomposition_energy_per_atom` | float | Decomposition energy per atom; ≤ 0 ⇒ on/under the convex hull (stable). |
| `decomposition_energy_relative` | float | Relative decomposition energy. |
| `bandgap_ev` | float | Electronic band gap (eV); ~0 ⇒ metallic/semimetallic. |
| `bandgap_type` | string | `metal`, `semiconductor`, … |
| `gnome_material_id` | string | Upstream GNoME/source material id. |
| `source` | string | Origin database (`Acadia Nanoforge Database`). |
| `data_version` | string | Source data version. |
| `created_at` | string | ISO timestamp of the source record. |

---

## 2 · `recipes` — workshop recipes (106,406 rows)

How to *make* it: an AI-drafted synthesis recipe per material. **Hypotheses, not validated
protocols** (see caveats in the README).

| Column | Type | Description |
|--------|------|-------------|
| `id` / `formula` | string | Join key. |
| `elements` | object | `{element: count}`. *(JSON string in Parquet/CSV.)* |
| `family` | string | Process family, e.g. `sulfide_other`, `oxide_silicate`, `metal_alloy`. |
| `family_reason` | string | Why that family was assigned. |
| `metal_sub_family` | string \| null | Alloy sub-family, when metallic. |
| `metal_supplier` | string \| null | Suggested metal-powder supplier note. |
| `alloy_validation` | string \| null | Alloy-plausibility note. |
| `batch_size_g` | int | Target batch mass (g). |
| `max_workshop_g` | int | Conservative workshop scale cap (g). |
| `scale_limit_reason` | string | Why the cap. |
| `ingredients` | list[object] | Each: `{element, precursor, name, mass_g, safety, supplier}`. *(JSON string in Parquet/CSV.)* |
| `firing_schedule` | object | `{peak_c, peak_range_c, hold_h, ramp, why}` or `{peak_c: null, why: "no template"}`. *(JSON string in Parquet/CSV.)* |
| `estimated_cost_eur` | float | Estimated precursor cost for the batch (EUR). |
| `confidence` | string | `HIGH` / `MEDIUM` / `LOW`. |
| `confidence_reason` | string | Basis for the confidence label. |
| `warnings` | list[string] | Recipe-level warnings. *(JSON string in Parquet/CSV.)* |
| `safety_flags` | list[string] | Per-ingredient hazard notes (guidance, not an SDS). *(JSON string in Parquet/CSV.)* |
| `db_temp_c` | int | Raw database firing temperature (°C) — uncorrected; see caveats. |
| `crystal_system`, `space_group` | string | Carried through from structure. |
| `bandgap_ev` | float | Carried through. |

---

## 3 · `scores` — scoring + categories (103,588 rows)

How a material ranks and what it is *for*, architecturally.

| Column | Type | Description |
|--------|------|-------------|
| `id` / `formula` | string | Join key. |
| `material_system` | string | e.g. `sulfide`, `oxide`, `intermetallic`. |
| `is_metallic` | bool | Metallic character. |
| `dimensionality` | string | Structural motif. |
| `db_temperature_c` | int | Raw database temperature (°C). |
| `corrected_temp_min_c` | int | Phase-corrected firing window, low end (°C). |
| `corrected_temp_max_c` | int | Phase-corrected firing window, high end (°C). |
| `temp_correction_note` | string | How the correction was derived. |
| `score_sustainability` | float | 0–10. |
| `score_structural` | float | 0–10. |
| `score_sensory` | float | 0–10. |
| `score_novelty` | float | 0–10. |
| `score_recipe_confidence` | float | 0–10. |
| `score_composite` | float | Weighted overall score, 0–10. |
| `architectural_categories` | list[string] | e.g. `["metallic/tension", "sulfide/lightweight"]`. *(JSON string in Parquet/CSV.)* |

---

## 4 · `architectural_candidates` — the short-list (15,984 rows)

The materials that passed the architectural filter: tiered, safety-screened, categorized.

| Column | Type | Description |
|--------|------|-------------|
| `id` / `formula` | string | Join key. |
| `reduced_formula` | string | Reduced formula. |
| `elements` | list[string] | Constituent elements. *(JSON string in Parquet/CSV.)* |
| `n_elements` | int | Element count. |
| `temperature` | int | Firing temperature (°C, source). |
| `duration_hours` | float | Hold duration (h). |
| `heating_rate` | float \| null | Ramp (°C/min) when given. |
| `cooling_method` | string | e.g. `natural`. |
| `density` | float | Raw source units (not g/cm³). |
| `crystal_system`, `space_group` | string | Structure. |
| `bandgap`, `bandgap_type` | float / string | Electronic. |
| `formation_energy` | float | Source units. |
| `decomposition_energy` | float | Source units. |
| `categories` | list[string] | Architectural use categories. *(JSON string in Parquet/CSV.)* |
| `safety_flags` | list[string] | Hazard notes (guidance). *(JSON string in Parquet/CSV.)* |
| `tier_score` | int | Filter tier (lower = stricter/closer to the top). |

---

## 5 · `atlas_published` — the printed selection (253 rows; 245 in the books)

The curated end of the pipeline, with **physical units and phase-corrected firing** — the
materials presented in the *Synthetic Types Atlas*. CSV (small enough to read directly).

| Column | Type | Description |
|--------|------|-------------|
| `formula` | string | Join key. |
| `assigned_lens`, `primary_lens` | string | Curatorial lens (theme) the material was placed under. |
| `rank_in_band` | int | Rank within its lens/band. |
| `family` | string | Process family. |
| `architectural_role` | string | Proposed architectural role. |
| `color` | string | Dominant fired colour. |
| `temp_tier` | string | Firing tier label. |
| `firing_peak_c` | int | **Phase-corrected** peak firing temperature (°C). |
| `cost_per_kg_eur` | float | Cost per kg (EUR). |
| `estimated_cost_eur` | float | Estimated batch cost (EUR). |
| `compress_mpa_est` | float | Estimated compressive strength (MPa). |
| `density_g_cm3` | float | **Physical** density (g/cm³). |
| `bandgap_ev` | float | Band gap (eV). |
| `est_co2_kg_kg` | float | Estimated embodied CO₂ (kg per kg). |
| `analog_honest` | string | Closest honest real-world analog. |
| `co2_vs_honest_pct` | float | CO₂ vs that analog (%). |
| `innovation_flags` | string | Notable properties. |
| `confidence` | string | Confidence label. |
| `kiln_tier` | string | Kiln class needed. |
| `chapter` | string | Book chapter/section. |
| `description` | string | One-line description. |
| `brennkurve_file` | string | Firing-curve image filename used in the book. |
| `in_printed_book` | `"true"`/`"false"` | Whether it appears in the printed books (8 are excluded). |

---

## Attribution

When you use the data, please credit: *Koehler, D. (2026). Generative Matter V3* (see
[`CITATION.cff`](CITATION.cff)), and acknowledge the upstream **GNoME** corpus
(Merchant et al., *Nature*, 2023). License: **CC BY-NC 4.0** (non-commercial, with credit).
