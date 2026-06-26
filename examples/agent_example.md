# Agent example — answering a question from the data

A short, end-to-end illustration of how an AI agent should use this dataset, including the
caveats it must carry into its answer.

### User question

> "I want a low-carbon material I could fire in a normal studio kiln (under ~1000 °C) and
> use structurally. Give me a couple of candidates with rough recipes."

### Agent procedure

1. **Rank by the right scores, in the right layer.** Use `scores` for `score_structural`
   and `score_sustainability`, and the *corrected* firing window — not the raw temperature.

   ```python
   import gzip, json
   def stream(layer):
       with gzip.open(f"data/{layer}.jsonl.gz", "rt", encoding="utf-8") as fh:
           for line in fh: yield json.loads(line)

   picks = [s for s in stream("scores")
            if (s["corrected_temp_max_c"] or 9999) <= 1000
            and (s["score_structural"] or 0) >= 8
            and (s["score_sustainability"] or 0) >= 7]
   picks.sort(key=lambda s: s["score_composite"] or 0, reverse=True)
   top = picks[:5]
   ```

2. **Attach the recipe** for each, from `recipes` (join on `formula`).

   ```python
   want = {s["formula"] for s in top}
   recipes = {r["formula"]: r for r in stream("recipes") if r["formula"] in want}
   ```

3. **Answer with the numbers — and the caveats.** For each candidate report the corrected
   firing window, the headline ingredients, the cost, and the confidence. Then state plainly:

   - these are **AI-generated hypotheses**, not tested protocols;
   - predicted stability is **not** a guarantee the compound can be synthesised as written;
   - the firing temperature is a **best-estimate** to validate on the first firing;
   - **safety flags are guidance** — check each precursor's SDS before handling.

### What a good answer looks like

> Two candidates from the dataset that fit (corrected firing ≤ 1000 °C, high structural +
> sustainability scores): **〈formula A〉** (composite 8.x; fires ~〈min–max〉 °C; ~€〈cost〉/batch;
> confidence MEDIUM) and **〈formula B〉** (…). Rough recipes below from the `recipes` layer.
> ⚠️ These are generated predictions: stability ≠ synthesizability, the temperatures are
> estimates to verify on a first firing, and the safety notes are not a substitute for each
> precursor's safety data sheet.

The point: the dataset gives you ranked, recipe-backed candidates fast — but the honesty
about what the numbers mean is part of the answer, not an afterthought.
