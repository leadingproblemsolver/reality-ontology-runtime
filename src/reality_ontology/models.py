from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class TruthState(str, Enum):
    DISCUSSED = "DISCUSSED"
    DECIDED = "DECIDED"
    PREPARED = "PREPARED"
    IMPLEMENTED = "IMPLEMENTED"
    TESTED = "TESTED"
    DEPLOYED = "DEPLOYED"
    EXPOSED = "EXPOSED"
    EXTERNALLY_USED = "EXTERNALLY_USED"
    REUSED = "REUSED"
    ADOPTED = "ADOPTED"
    PAID = "PAID"
    OUTCOME_PRODUCING = "OUTCOME_PRODUCING"

TRUTH_ORDER = list(TruthState)

class EpistemicType(str, Enum):
    FACT = "FACT"
    USER_REPORTED_FACT = "USER_REPORTED_FACT"
    OBSERVATION = "OBSERVATION"
    DECISION = "DECISION"
    HYPOTHESIS = "HYPOTHESIS"
    INFERENCE = "INFERENCE"
    SPECULATION = "SPECULATION"
    UNKNOWN = "UNKNOWN"

class RiskLevel(str, Enum):
    L0_READ = "L0_READ"
    L1_REVERSIBLE_WRITE = "L1_REVERSIBLE_WRITE"
    L2_EXTERNAL_CONSEQUENTIAL = "L2_EXTERNAL_CONSEQUENTIAL"

class AttemptStatus(str, Enum):
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    WAITING_EXTERNAL = "WAITING_EXTERNAL"
    SUSPENDED = "SUSPENDED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_TERMINAL = "FAILED_TERMINAL"
    SUCCEEDED_UNVERIFIED = "SUCCEEDED_UNVERIFIED"
    VERIFIED = "VERIFIED"
    SETTLED = "SETTLED"

@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    evidence_type: str
    source_locator: str
    observation: str
    digest: str
    captured_at: str
    trust: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class RealityEvent:
    event_id: str
    occurred_at: str
    actor_id: str
    object_id: str
    event_type: str
    previous_state: str | None
    resulting_state: str | None
    goal_id: str | None
    evidence_ids: list[str]
    source: str
    confidence: float = 1.0
    epistemic_type: EpistemicType = EpistemicType.OBSERVATION
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TransitionContract:
    transition_id: str
    object_id: str
    goal_id: str | None
    entry_state: str | None
    desired_state: str
    operator: str
    operation: str
    proof_required: str
    risk: RiskLevel
    preconditions: list[str] = field(default_factory=list)
    evidence_basis: list[str] = field(default_factory=list)
    maximum_scope: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    rollback: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class OperatorResult:
    result: dict[str, Any]
    side_effect_possible: bool = False

@dataclass(frozen=True)
class VerificationResult:
    verified: bool
    observation: str
    source_locator: str
    metadata: dict[str, Any] = field(default_factory=dict)
