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
- a projection receipt containing source hashes, source identity, run parameters, and output counts;
- an input preflight receipt that exposes workbook sheets, selected sheet, discovered headers, canonical mappings, missing required fields, and unsupported fields before projection;
- when `--with-impact` is used, a separate deterministic `engineer_review.csv` copy with empty reviewer fields for external correction.

It does **not** claim that the future schedule is fact. It is a deterministic projection of the supplied schedule snapshot.

## Run the fixture

```bash
pip install -e '.[xlsx]'

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
  input_preflight.json
  90_day_readiness.csv
  schedule_changes.csv
  change_impact.csv
  engineer_review.csv
  projection_receipt.json
```

`--with-impact` requires `--previous-activities` because the combined view is explicitly a before/current comparison, not a synthetic change guess.

## Real-cycle one-command handoff

For one anonymized engineer planning cycle, keep the existing command and replace only the file paths and `--as-of` date:

```bash
ro construction-lookahead \
  --activities /path/to/current_p6_activities.xlsx \
  --relationships /path/to/current_relationships.xlsx \
  --requirements /path/to/qa_document_requirements.xlsx \
  --previous-activities /path/to/previous_schedule_snapshot.xlsx \
  --with-impact \
  --as-of YYYY-MM-DD \
  --days 90 \
  --output-dir artifacts/engineer-real-cycle
```

The handoff wrapper delegates to the existing deterministic projection engine. It does not create a second construction engine or infer new scheduling semantics.

## Real-input preflight

Before projection, each source is inspected without silently changing semantics.

For CSV, preflight records:

- discovered headers;
- canonical mappings;
- missing required fields;
- unsupported fields.

For XLSX/XLSM, it additionally records:

- every worksheet name;
- the worksheet the existing importer would select (currently the first worksheet);
- headers/mappings/missing fields for every worksheet.

If the selected worksheet or headers do not satisfy the current contract, projection fails and `input_preflight.json` remains behind as the inspection receipt. The system does not guess a different worksheet or invent a header mapping. A real export is required before adding the smallest necessary alias or explicit sheet selection.

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

## Engineer review artifact

`engineer_review.csv` is generated from `change_impact.csv` after the machine output has been written. The canonical `change_impact.csv` is not mutated.

The review copy appends three empty fields:

```text
engineer_verdict      # ACCEPT | CORRECT | REJECT, entered by the engineer
engineer_correction   # corrected interpretation/value when applicable
engineer_note         # short explanation/evidence
```

The system never pre-populates these fields. They exist only to collect external review.

## XLSX input

CSV keeps the fixture inspectable in Git. Real exports can be `.xlsx` or `.xlsm`:

```bash
pip install -e '.[xlsx]'
```

The current importer uses the first worksheet and header aliases for common activity fields. Real P6 exports remain the next evidence event: field aliases, explicit sheet selection, and relationship semantics should be changed only after seeing the engineer's anonymized exports.

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

### Safe anonymization

Company, project, client, package, person, and free-text names may be anonymized where they are not required for the test.

The following must remain internally consistent because the execution path depends on them:

```text
activity IDs
predecessor/successor relationships
planned dates and statuses
WBS identifiers used for requirement mapping
activity/WBS requirement scope identifiers
lead-day values when they are part of the engineer's actual rule
```

Do not replace missing fields with guessed values. If anonymization breaks referential consistency, the run is not a valid real-cycle test.

## Hard failure conditions

The slice refuses to silently continue when:

- the selected worksheet/header contract fails preflight;
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
- The importer still selects the first worksheet; preflight exposes all worksheets but deliberately does not guess another sheet.
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

Return `engineer_review.csv` to the engineer and ask him to mark each disputed row `ACCEPT`, `CORRECT`, or `REJECT` with a short correction/note.

The product claim must not advance beyond `TESTED` until a real cycle executes and the engineer supplies a correction, acceptance, or technical rejection.
