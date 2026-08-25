import pytest
from reality_ontology.executor import ApprovalRequired, ExecutionEngine
from reality_ontology.models import OperatorResult, RiskLevel, TransitionContract, VerificationResult
from reality_ontology.operators.base import Operator
from reality_ontology.store import RealityStore

class ExternalOperator(Operator):
    name = "external.mock"
    risk = RiskLevel.L2_EXTERNAL_CONSEQUENTIAL
    def execute(self, contract, prepared): return OperatorResult({"id":"external-1"}, side_effect_possible=True)
    def verify(self, contract, execution): return VerificationResult(True, "fresh external reread confirmed", "external://1")


def test_external_requires_approval(tmp_path):
    with RealityStore(tmp_path / "r.db") as s:
        actor = s.add_actor("human")
        obj = s.add_object("external:1", "remote")
        ev = s.add_evidence("observation", "external://1", "ready")
        s.record_event(actor_id=actor, object_id=obj, event_type="seed", resulting_state="READY", evidence_ids=[ev])
        c = TransitionContract("tx", obj, None, "READY", "CHANGED", "external.mock", "mutate", "fresh reread", RiskLevel.L2_EXTERNAL_CONSEQUENTIAL)
        engine = ExecutionEngine(s, [ExternalOperator()])
        with pytest.raises(ApprovalRequired):
            engine.execute(c, inputs={}, actor_id=actor)
        s.approve("tx", actor)
        engine.execute(c, inputs={}, actor_id=actor)
        assert s.current_state(obj) == "CHANGED"


def test_relation_requires_evidence(tmp_path):
    with RealityStore(tmp_path / "r.db") as s:
        with pytest.raises(ValueError): s.relate("a", "depends_on", "b", [])
