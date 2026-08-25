from reality_ontology.cli import _demo


def test_demo_does_not_repeat_settled_transition(tmp_path):
    db = str(tmp_path / "reality.db")
    first = _demo(db)
    second = _demo(db)
    assert first["acceptance"] is True
    assert second["execution"] == "NOOP_ALREADY_SETTLED"
