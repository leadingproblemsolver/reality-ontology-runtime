from pathlib import Path
import pytest
from reality_ontology.store import RealityStore
from reality_ontology.truth import TruthPromotionError


def test_state_is_derived_from_evidence_events(tmp_path):
    db = tmp_path / "r.db"
    with RealityStore(db) as s:
        actor = s.add_actor("tester")
        goal = s.add_goal("contacted", "submission receipt")
        obj = s.add_object("prospect:8", "prospect")
        ev = s.add_evidence("external_receipt", "browser://receipt", "submission confirmation observed")
        s.record_event(actor_id=actor, object_id=obj, goal_id=goal, event_type="form_submitted", resulting_state="CONTACTED", evidence_ids=[ev])
        assert s.current_state(obj) == "CONTACTED"
        assert len(s.timeline(obj)) == 1


def test_event_cannot_reference_missing_evidence(tmp_path):
    with RealityStore(tmp_path / "r.db") as s:
        actor = s.add_actor("tester")
        obj = s.add_object("x", "artifact")
        with pytest.raises(ValueError):
            s.record_event(actor_id=actor, object_id=obj, event_type="fake", resulting_state="TESTED", evidence_ids=["missing"])


def test_truth_ladder_blocks_unproven_deployment(tmp_path):
    with RealityStore(tmp_path / "r.db") as s:
        actor = s.add_actor("tester")
        obj = s.add_object("repo:x", "artifact")
        ev = s.add_evidence("test_result", "pytest://run", "tests passed")
        s.record_event(actor_id=actor, object_id=obj, event_type="tests", resulting_state="TESTED", evidence_ids=[ev])
        weak = s.add_evidence("observation", "local://claim", "deploy command typed")
        with pytest.raises(TruthPromotionError):
            s.record_event(actor_id=actor, object_id=obj, event_type="deploy_claim", resulting_state="DEPLOYED", evidence_ids=[weak])
