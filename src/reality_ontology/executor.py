from __future__ import annotations
from typing import Any
from .models import AttemptStatus, RiskLevel, TransitionContract
from .store import RealityStore
from .operators.base import Operator

class ApprovalRequired(PermissionError): pass
class PreconditionsFailed(RuntimeError): pass
class VerificationFailed(RuntimeError): pass

class ExecutionEngine:
    def __init__(self, store: RealityStore, operators: list[Operator]):
        self.store = store
        self.operators = {o.name: o for o in operators}

    def execute(self, contract: TransitionContract, *, inputs: dict[str, Any], actor_id: str, owner: str | None = None, next_transition: str | None = None, next_action: str | None = None) -> dict[str, Any]:
        op = self.operators.get(contract.operator)
        if not op: raise KeyError(f"operator not registered: {contract.operator}")
        if op.risk != contract.risk:
            raise ValueError(f"contract/operator risk mismatch: {contract.risk} != {op.risk}")
        if contract.risk == RiskLevel.L2_EXTERNAL_CONSEQUENTIAL and not self.store.is_approved(contract.transition_id):
            raise ApprovalRequired(contract.transition_id)

        prior = self.store.current_state(contract.object_id)
        if contract.entry_state is not None and prior != contract.entry_state:
            raise PreconditionsFailed(f"entry state mismatch: expected {contract.entry_state!r}, got {prior!r}")

        attempt_id = self.store.begin_attempt(contract.transition_id, f"{contract.operator}:{contract.operation}", inputs, actor_id)
        prepared = op.prepare(contract, inputs)
        execution = op.execute(contract, prepared)
        self.store.update_attempt(attempt_id, AttemptStatus.SUCCEEDED_UNVERIFIED, result=execution.result, external_side_effect=execution.side_effect_possible, checkpoint="execution_returned")

        verification = op.verify(contract, execution)
        evidence_id = self.store.add_evidence(
            evidence_type="external_receipt" if contract.risk == RiskLevel.L2_EXTERNAL_CONSEQUENTIAL else "verification_receipt",
            source_locator=verification.source_locator,
            observation=verification.observation,
            metadata=verification.metadata,
        )
        if not verification.verified:
            self.store.update_attempt(attempt_id, AttemptStatus.FAILED_RETRYABLE, evidence_ids=[evidence_id], failure_class="verification_failed", checkpoint="reread_complete")
            raise VerificationFailed(verification.observation)

        self.store.update_attempt(attempt_id, AttemptStatus.VERIFIED, evidence_ids=[evidence_id], checkpoint="verified")
        event_id = self.store.record_event(
            actor_id=actor_id, object_id=contract.object_id, goal_id=contract.goal_id,
            event_type="transition_verified", resulting_state=contract.desired_state,
            evidence_ids=[evidence_id], source=verification.source_locator,
            metadata={"transition_id": contract.transition_id, "attempt_id": attempt_id}
        )
        settlement_id = self.store.settle(
            run_id=attempt_id, prior_state=prior, action_taken=f"{contract.operator}:{contract.operation}",
            observed_result=verification.observation, evidence_ids=[evidence_id], new_state=contract.desired_state,
            next_transition=next_transition, next_action=next_action, owner=owner or actor_id, context_updated=True
        )
        self.store.update_attempt(attempt_id, AttemptStatus.SETTLED, evidence_ids=[evidence_id], checkpoint="settled", state_mutation={"event_id": event_id, "new_state": contract.desired_state, "settlement_id": settlement_id})
        return {"attempt_id": attempt_id, "event_id": event_id, "evidence_id": evidence_id, "settlement_id": settlement_id, "new_state": contract.desired_state}
