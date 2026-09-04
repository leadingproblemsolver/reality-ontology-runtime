# Construction Planning Assumptions

## Combined change-impact cardinality

ASSUMPTION: One `change_impact.csv` row represents one schedule-change record × one current readiness/requirement row.
SOURCE: none — engineering default.
WHY NEEDED: A changed activity can have multiple schedule-change records and multiple mapped requirements. The combined view needs deterministic cardinality without silently collapsing or duplicating evidence.
CURRENT BEHAVIOR: Each change is joined to every current readiness/requirement row for the same activity. Ordering is deterministic. A changed activity with no current readiness row still produces one row with `effect_evidence=UNRESOLVED`.
WHAT WOULD CHANGE IT: Engineer feedback or a real P6/QA cycle showing that changes should instead be aggregated into a different operator-facing unit.

## Changed activity without a current readiness row

ASSUMPTION: A schedule change should remain visible even when the changed activity has no current 90-day readiness row.
SOURCE: none — engineering default.
WHY NEEDED: Dropping the change would hide real schedule movement merely because the activity is removed, outside the lookahead, complete, or otherwise absent from the current readiness projection.
CURRENT BEHAVIOR: The change remains in `change_impact.csv`; previous/current activity provenance is retained where available and the downstream effect is marked `UNRESOLVED`.
WHAT WOULD CHANGE IT: Real workflow evidence showing that a specific class of out-of-window/removed changes should be excluded from the engineer-facing combined view.
