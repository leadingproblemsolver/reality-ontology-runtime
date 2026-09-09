import json
from datetime import date
from pathlib import Path

import pytest

from reality_ontology.domains.construction_planning import ConstructionInputError, run_lookahead


def _write(path: Path, text: str) -> Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def test_unreadable_xlsx_leaves_failure_receipt_and_retry_can_succeed(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")

    current = tmp_path / "current.xlsx"
    current.write_bytes(b"not-an-xlsx-workbook")
    previous = _write(
        tmp_path / "previous.csv",
        """
Activity ID,Activity Name,WBS,Planned Start,Planned Finish,Status
A110,Waterproofing,B01,2026-10-15,2026-10-25,Not Started
""",
    )
    relationships = _write(
        tmp_path / "relationships.csv",
        """
Predecessor ID,Successor ID
""",
    )
    requirements = _write(
        tmp_path / "requirements.csv",
        """
Scope Type,Scope ID,Requirement,Lead Days
activity,A110,WIR + waterproofing checklist,14
""",
    )
    output = tmp_path / "out"

    kwargs = dict(
        activities_path=str(current),
        relationships_path=str(relationships),
        requirements_path=str(requirements),
        previous_activities_path=str(previous),
        with_impact=True,
        as_of=date(2026, 9, 4),
        days=90,
        output_dir=str(output),
    )

    with pytest.raises(ConstructionInputError, match="real-input preflight failed"):
        run_lookahead(**kwargs)

    failed = json.loads((output / "input_preflight.json").read_text(encoding="utf-8"))
    assert failed["status"] == "FAIL"
    assert failed["sources"]["activities"]["status"] == "FAIL"
    assert "could not read XLSX source" in failed["sources"]["activities"]["error"]
    assert not (output / "projection_receipt.json").exists()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Activities"
    sheet.append(["Activity ID", "Activity Name", "WBS", "Planned Start", "Planned Finish", "Status"])
    sheet.append(["A110", "Waterproofing", "B01", "2026-09-15", "2026-09-25", "Not Started"])
    workbook.save(current)

    receipt = run_lookahead(**kwargs)
    recovered = json.loads((output / "input_preflight.json").read_text(encoding="utf-8"))

    assert recovered["status"] == "PASS"
    assert receipt["impact_rows"] > 0
    assert (output / "90_day_readiness.csv").exists()
    assert (output / "change_impact.csv").exists()
    assert (output / "engineer_review.csv").exists()
    assert (output / "projection_receipt.json").exists()
