from __future__ import annotations
from pathlib import Path
from typing import Any
from .base import Operator
from ..models import OperatorResult, RiskLevel, TransitionContract, VerificationResult


class FileMarkerOperator(Operator):
    name = "filesystem.append_marker"
    risk = RiskLevel.L1_REVERSIBLE_WRITE

    def execute(self, contract: TransitionContract, prepared: dict[str, Any]) -> OperatorResult:
        path = Path(prepared["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        marker = prepared["marker"]
        with path.open("a", encoding="utf-8") as f:
            f.write(marker + "\n")
        return OperatorResult(
            result={"path": str(path), "marker": marker},
            side_effect_possible=True,
        )

    def verify(self, contract: TransitionContract, execution: OperatorResult) -> VerificationResult:
        path = Path(execution.result["path"])
        marker = execution.result["marker"]
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        verified = marker in text.splitlines()
        return VerificationResult(
            verified=verified,
            observation=f"marker {'found' if verified else 'not found'} in fresh reread",
            source_locator=str(path),
            metadata={"marker": marker},
        )
