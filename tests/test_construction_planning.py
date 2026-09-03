from datetime import date
from pathlib import Path

import pytest

from reality_ontology.domains.construction_planning import (
    ConstructionInputError,
    diff_activities,
    load_activities,
    load_relations,
    load_requirements,
    project_lookahead,
)


def write(path: Path, text: str) -> Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def fixtures(tmp_path: Path):
    activities = write(tmp_path / "activities.csv", """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A100,Structure complete,B05,2026-09-01,2026-09-10,Complete
A110,Waterproofing,B05,2026-09-15,2026-09-25,Not Started
A120,Ceiling closeout,B05,2026-10-20,2026-10-30,Not Started
A130,External works,B07,2027-01-15,2027-02-15,Not Started
""")
    relations = write(tmp_path / "relationships.csv", """
Predecessor ID,Successor ID
A100,A110
A110,A120
""")
    requirements = write(tmp_path / "requirements.csv", """
Scope Type,Scope ID,Requirement,Lead Days
activity,A110,WIR + waterproofing checklist,14
wbs,B05,QA closeout package,14
""")
    return activities, relations, requirements


def test_projects_only_overlapping_lookahead_and_flags_blocker(tmp_path):
    activities, relations, requirements = fixtures(tmp_path)
    rows = project_lookahead(
        load_activities(activities),
        load_relations(relations),
        load_requirements(requirements),
        as_of=date(2026, 9, 4),
        days=90,
    )
    by_activity = {row.activity_id: row for row in rows}
    assert "A130" not in by_activity
    assert by_activity["A110"].readiness_status == "PREPARE_NOW"
    assert by_activity["A110"].requirement == "WIR + waterproofing checklist"
    assert by_activity["A120"].readiness_status == "BLOCKED"
    assert by_activity["A120"].blocking_predecessors == "A110"
    assert "#row=" in by_activity["A120"].source_activity


def test_rejects_unknown_relationship(tmp_path):
    activities, _, requirements = fixtures(tmp_path)
    relations = write(tmp_path / "bad_rel.csv", """
Predecessor ID,Successor ID
A999,A110
""")
    with pytest.raises(ConstructionInputError, match="unknown activity"):
        project_lookahead(
            load_activities(activities),
            load_relations(relations),
            load_requirements(requirements),
            as_of=date(2026, 9, 4),
        )


def test_rejects_duplicate_activity_ids(tmp_path):
    activities = write(tmp_path / "dup.csv", """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A1,One,B1,2026-09-05,2026-09-06,Not Started
A1,Duplicate,B1,2026-09-05,2026-09-06,Not Started
""")
    with pytest.raises(ConstructionInputError, match="duplicate activity_id"):
        load_activities(activities)


def test_diff_surfaces_schedule_movement_and_window_entry(tmp_path):
    previous = write(tmp_path / "previous.csv", """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A1,Final inspection,B1,2026-12-20,2026-12-22,Not Started
""")
    current = write(tmp_path / "current.csv", """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A1,Final inspection,B1,2026-11-20,2026-11-22,Not Started
""")
    changes = diff_activities(
        load_activities(previous),
        load_activities(current),
        as_of=date(2026, 9, 4),
        days=90,
    )
    change_types = {c["change"] for c in changes}
    assert "START_MOVED" in change_types
    assert "FINISH_MOVED" in change_types
    assert "ENTERED_LOOKAHEAD" in change_types
