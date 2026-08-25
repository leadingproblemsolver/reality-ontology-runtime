from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..models import OperatorResult, RiskLevel, TransitionContract, VerificationResult

class Operator(ABC):
    name: str
    risk: RiskLevel

    def prepare(self, contract: TransitionContract, inputs: dict[str, Any]) -> dict[str, Any]:
        return inputs

    @abstractmethod
    def execute(self, contract: TransitionContract, prepared: dict[str, Any]) -> OperatorResult: ...

    @abstractmethod
    def verify(self, contract: TransitionContract, execution: OperatorResult) -> VerificationResult: ...

    def rollback(self, contract: TransitionContract, execution: OperatorResult) -> bool:
        return False
