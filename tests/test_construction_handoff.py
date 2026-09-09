import json
from datetime import date
from pathlib import Path

import pytest

from reality_ontology.domains.construction_planning import ConstructionInputError, inspect_source, run_lookahead


def write(path: Path, text: str) -> Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def real_cycle_files(tmp_path: Path):
    current = write(
        tmp_path / "current.csv",
        """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A100,Structure,B01,2026-09-01,2026-09-10,Complete
A110,Waterproofing,B01,2026-09-15,2026-09-25,Not Started
A120,Ceiling closeout,B01,2026-10-20,2026-10-30,Not Started
""",
    )
    previous = write(
        tmp_path / "previous.csv",
        """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A100,Structure,B01,2026-09-01,2026-09-10,Complete
A110,Waterproofing,B01,2026-10-15,2026-10-25,Not Started
A120,Ceiling closeout,B01,2026-10-20,2026-10-30,Not Started
""",
    )
    relationships = write(
        tmp_path / "relationships.csv",
        """
Predecessor ID,Successor ID
A100,A110
A110,A120
""",
    )
    requirements = write(
        tmp_path / "requirements.csv",
        """
Scope Type,Scope ID,Requirement,Lead Days
activity,A110,WIR + waterproofing checklist,14
wbs,B01,QA closeout package,14
""",
    )
    return current, relationships, requirements, previous


def run_cycle(tmp_path: Path):
    current, relationships, requirements, previous = real_cycle_files(tmp_path)
    output = tmp_path / "out"
    receipt = run_lookahead(
        activities_path=str(current),
        relationships_path=str(relationships),
        requirements_path=str(requirements),
        previous_activities_path=str(previous),
        with_impact=True,
        as_of=date(2026, 9, 4),
        days=90,
        output_dir=str(output),
    )
    return receipt, output


def test_real_cycle_handoff_emits_preflight_review_and_reproducible_receipt(tmp_path):
    receipt, output = run_cycle(tmp_path)

    preflight = json.loads((output / "input_preflight.json").read_text(encoding="utf-8"))
    assert preflight["status"] == "PASS"
    assert preflight["sources"]["activities"]["canonical_mappings"]["activity_id"] == "Activity ID"

    machine_before = (output / "change_impact.csv").read_bytes()
    review = (output / "engineer_review.csv").read_text(encoding="utf-8")
    machine_after = (output / "change_impact.csv").read_bytes()
    assert machine_before == machine_after
    assert "engineer_verdict" in review.splitlines()[0]
    assert "engineer_correction" in review.splitlines()[0]
    assert "engineer_note" in review.splitlines()[0]

    assert receipt["source_identity"]["activities"]["path"].endswith("current.csv")
    assert receipt["source_identity"]["activities"]["sha256"] == receipt["source_hashes"]["activities"]
    assert receipt["outputs"]["preflight_json"].endswith("input_preflight.json")
    assert receipt["outputs"]["engineer_review_csv"].endswith("engineer_review.csv")


def test_missing_required_column_fails_after_saving_preflight(tmp_path):
    current, relationships, requirements, previous = real_cycle_files(tmp_path)
    current.write_text(
        "Activity ID,Activity Name,WBS,Planned Start,Planned Finish\n"
        "A110,Waterproofing,B01,2026-09-15,2026-09-25\n",
        encoding="utf-8",
    )
    output = tmp_path / "out"

    with pytest.raises(ConstructionInputError, match="real-input preflight failed"):
        run_lookahead(
            activities_path=str(current),
            relationships_path=str(relationships),
            requirements_path=str(requirements),
            previous_activities_path=str(previous),
            with_impact=True,
            as_of=date(2026, 9, 4),
            output_dir=str(output),
        )

    preflight = json.loads((output / "input_preflight.json").read_text(encoding="utf-8"))
    assert preflight["status"] == "FAIL"
    assert preflight["sources"]["activities"]["missing_required_fields"] == ["status"]
    assert not (output / "90_day_readiness.csv").exists()


def test_repeated_handoff_execution_is_deterministic(tmp_path):
    receipt, output = run_cycle(tmp_path)
    first = {
        "preflight": (output / "input_preflight.json").read_bytes(),
        "readiness": (output / "90_day_readiness.csv").read_bytes(),
        "changes": (output / "schedule_changes.csv").read_bytes(),
        "impact": (output / "change_impact.csv").read_bytes(),
        "review": (output / "engineer_review.csv").read_bytes(),
        "receipt": (output / "projection_receipt.json").read_bytes(),
    }

    current = Path(receipt["source_identity"]["activities"]["path"])
    relationships = Path(receipt["source_identity"]["relationships"]["path"])
    requirements = Path(receipt["source_identity"]["requirements"]["path"])
    previous = Path(receipt["source_identity"]["previous_activities"]["path"])
    run_lookahead(
        activities_path=str(current),
        relationships_path=str(relationships),
        requirements_path=str(requirements),
        previous_activities_path=str(previous),
        with_impact=True,
        as_of=date(2026, 9, 4),
        days=90,
        output_dir=str(output),
    )

    second = {
        name: (output / filename).read_bytes()
        for name, filename in {
            "preflight": "input_preflight.json",
            "readiness": "90_day_readiness.csv",
            "changes": "schedule_changes.csv",
            "impact": "change_impact.csv",
            "review": "engineer_review.csv",
            "receipt": "projection_receipt.json",
        }.items()
    }
    assert first == second


def test_xlsx_preflight_reports_selected_sheet_headers_and_unsupported_fields(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Activities"
    sheet.append(["Activity ID", "Activity Name", "WBS", "Planned Start", "Planned Finish", "Status", "Project Name"])
    sheet.append(["A1", "Test", "B1", "2026-09-10", "2026-09-11", "Not Started", "REDACTED"])
    source = tmp_path / "activities.xlsx"
    workbook.save(source)

    report = inspect_source(source, "activities")
    assert report["status"] == "PASS"
    assert report["worksheet_names"] == ["Activities"]
    assert report["selected_worksheet"] == "Activities"
    assert report["canonical_mappings"]["planned_start"] == "Planned Start"
    assert report["unsupported_fields"] == ["Project Name"]


def test_unknown_first_worksheet_fails_with_all_sheet_evidence(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    workbook = openpyxl.Workbook()
    notes = workbook.active
    notes.title = "Notes"
    notes.append(["Project", "Prepared By"])
    activities = workbook.create_sheet("Activities")
    activities.append(["Activity ID", "Activity Name", "WBS", "Planned Start", "Planned Finish", "Status"])
    activities.append(["A1", "Test", "B1", "2026-09-10", "2026-09-11", "Not Started"])
    current = tmp_path / "current.xlsx"
    workbook.save(current)

    _, relationships, requirements, previous = real_cycle_files(tmp_path)
    output = tmp_path / "out"
    with pytest.raises(ConstructionInputError, match="real-input preflight failed"):
        run_lookahead(
            activities_path=str(current),
            relationships_path=str(relationships),
            requirements_path=str(requirements),
            previous_activities_path=str(previous),
            with_impact=True,
            as_of=date(2026, 9, 4),
            output_dir=str(output),
        )

    preflight = json.loads((output / "input_preflight.json").read_text(encoding="utf-8"))
    source = preflight["sources"]["activities"]
    assert source["selected_worksheet"] == "Notes"
    assert source["worksheet_names"] == ["Notes", "Activities"]
    assert source["worksheets"][0]["missing_required_fields"]
    assert source["worksheets"][1]["missing_required_fields"] == []
