# Construction Planning MVP — 90-Day Readiness Projection

## Source-derived workflow

This vertical slice is based on one planning engineer's described loop:

`fragmented Excel data -> Primavera schedule + activity relationships -> maintained project plan -> department-specific future lookahead`

The first slice targets the explicit quality/documentation request: identify activities in the next three months and map the documentation/inspection preparation required before those activities occur.

## What this implementation does

Given:

1. an activity export;
2. an activity-relationship export;
3. a QA/document requirement mapping;
4. optionally, a previous activity snapshot;

it deterministically produces:

- every non-complete activity whose planned interval overlaps the lookahead window;
- unresolved predecessor blockers;
- the applicable activity- or WBS-scoped requirement;
- a preparation date derived from an explicit departmental lead-time rule;
- `PREPARE_NOW`, `UPCOMING`, `BLOCKED`, or `REQUIREMENT_UNMAPPED` status;
- source file, source row, and source SHA-256 provenance for each projected row;
- schedule movement between snapshots (`START_MOVED`, `FINISH_MOVED`, `STATUS_CHANGED`, `ENTERED_LOOKAHEAD`, etc.);
- optionally, a combined `change_impact.csv` that joins each schedule-change record to the current readiness/requirement row it affects;
- a projection receipt containing source hashes and output counts.

It does **not** claim that the future schedule is fact. It is a deterministic projection of the supplied schedule snapshot.

## Run the fixture

```bash
pip install -e .

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

`--with-impact` requires `--previous-activities` because the combined view is explicitly a before/current comparison, not a synthetic change guess.

## Combined change-impact contract

`change_impact.csv` is deliberately narrow. It does not implement a second change-propagation engine.

The row contract is:

`one schedule-change record × one current readiness/requirement row`

For each row it carries:

- the original schedule change (`before`, `after`, optional `delta_days`);
- previous/current activity source references when available;
- current readiness status and blockers;
- requirement and action date when mapped;
- `effect_evidence = KNOWN` when the downstream preparation effect has a source requirement;
- `effect_evidence = UNRESOLVED` when requirement evidence is absent or there is no current readiness row;
- current activity and requirement provenance.

This preserves two facts when they co-occur. For example, an activity may remain `BLOCKED` because its predecessor is incomplete while its requirement mapping is still unresolved. The readiness status is not rewritten; the missing requirement remains visible through `effect_evidence=UNRESOLVED` and an empty requirement source.

A changed activity is never dropped merely because it has no current readiness row. It remains in the combined output with the downstream effect explicitly unresolved.

## XLSX input

CSV keeps the fixture inspectable in Git. Real exports can be `.xlsx` or `.xlsm`:

```bash
pip install -e '.[xlsx]'
```

The current importer uses the first worksheet and header aliases for common activity fields. Real P6 exports are the next evidence event: field aliases and sheet selection should be changed only after seeing the engineer's anonymized exports.

## Current input contract

### Activities

Required canonical fields (common aliases accepted):

```text
Activity ID
Activity Name
WBS
Planned Start
Planned Finish
Status
```

### Relationships

```text
Predecessor ID
Successor ID
```

### Requirements

```text
Scope Type      # activity | wbs
Scope ID
Requirement
Lead Days       # optional, defaults to 0
```

`Lead Days` is an explicit operational rule, not an inferred AI value.

## Hard failure conditions

The slice currently refuses to silently continue when:

- duplicate activity IDs exist;
- a relationship references an unknown activity;
- planned finish precedes planned start;
- required columns are absent;
- dates cannot be parsed;
- unsupported requirement scope is supplied;
- `--with-impact` is requested without a previous activity snapshot.

## Known limitations

- Relationship type and lag semantics (FS/SS/FF/SF and lag) are not modeled in this slice.
- The importer has not yet been verified against the engineer's real P6 export schema.
- The combined impact view links a changed activity to the readiness/requirement rows already produced by the current projection; it does not infer broader causal propagation beyond the relationships and requirements already modeled.

These limitations remain explicit rather than being resolved by guesswork.

## Why this is not an agent

There is no LLM in the projection path. The MVP first tests whether deterministic reconstruction and change detection reduce the engineer's schedule-maintenance burden. An LLM is allowed later only where the real workflow exposes ambiguous interpretation that deterministic evidence cannot resolve.

## Next external evidence event

Run this against one anonymized real cycle containing:

- current P6 activity export;
- current activity-relationship export;
- previous schedule snapshot;
- the QA/document file the engineer normally merges.

Compare his normal preparation time and corrections against this projection. The product claim should not advance beyond `TESTED` until that happens.
