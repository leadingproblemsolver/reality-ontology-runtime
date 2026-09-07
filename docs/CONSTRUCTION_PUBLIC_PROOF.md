# Construction planning public proof

This is the narrow public proof surface for PR #13.

## Problem

Given a current activity snapshot, relationships, a previous snapshot, and QA/document requirements, deterministically surface what changed, what is blocked, what preparation is required, and where each conclusion came from.

## Reproduce

Requirements: Python 3.11+

```bash
git clone https://github.com/leadingproblemsolver/reality-ontology-runtime.git
cd reality-ontology-runtime
git checkout feat/construction-lookahead-mvp
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ro construction-lookahead \
  --activities examples/construction/activities.csv \
  --relationships examples/construction/relationships.csv \
  --requirements examples/construction/qa_requirements.csv \
  --previous-activities examples/construction/previous_activities.csv \
  --with-impact \
  --as-of 2026-09-04 \
  --days 90 \
  --output-dir artifacts/construction-demo
```

Expected outputs:

```text
artifacts/construction-demo/
  90_day_readiness.csv
  schedule_changes.csv
  change_impact.csv
  projection_receipt.json
```

## Verified receipt

PR head at verification: `81b253c2b62a095278973c2477a67c3dbc3a1da5`

GitHub Actions `ci` run #87 (`33886755370`) completed successfully.

On that run:

- clean editable install succeeded;
- `pytest` -> **28 passed in 1.59s**;
- repository demo completed successfully and reconstructed its settled state after restart.

The construction regression also requires generated `change_impact.csv` to match the checked-in golden fixture and requires a second run to be byte-identical to the first.

## Inspectable output

The checked-in synthetic fixture produces 7 schedule-change -> impact rows.

A130 is the clearest example:

- planned start moved from 2026-12-20 to 2026-11-20 (`delta_days=-30`);
- the activity entered the 90-day lookahead;
- readiness remains `BLOCKED` by A120;
- the mapped requirement is `Final inspection dossier`;
- `effect_evidence=KNOWN`;
- previous/current activity and requirement source references are retained in the output.

See: [`examples/construction/expected/change_impact.csv`](../examples/construction/expected/change_impact.csv)

## Evidence boundary

This proof is **synthetic only**. It does not claim:

- verification against a real Primavera P6 export schema;
- correctness on a live project;
- engineer validation;
- production use;
- measured time saving or accuracy improvement;
- adoption or commercial value.

Relationship type and lag semantics (FS/SS/FF/SF + lag) are deliberately unsupported until real workflow evidence requires them.

## Next evidence event

Run the existing pipeline unchanged against one anonymized real planning cycle containing:

1. current P6 activities export;
2. current relationship export;
3. previous schedule snapshot;
4. the QA/document file the engineer normally merges.

Promotion criterion: the engineer accepts, corrects, or rejects the source-linked output against that real planning cycle.
