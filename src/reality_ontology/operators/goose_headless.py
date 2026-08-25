from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .base import Operator
from ..models import OperatorResult, RiskLevel, TransitionContract, VerificationResult
from ..verification import verify_spec


class GooseHeadlessOperator(Operator):
    """Execute bounded Goose work, then verify through a fresh deterministic reread.

    Two execution modes are supported:
    - task mode: Goose's built-in developer extension
    - recipe mode: an explicit Goose recipe, including tightly scoped MCP extensions

    The operator remains L2 because either mode can cause external consequences.
    """

    name = "goose.headless"
    risk = RiskLevel.L2_EXTERNAL_CONSEQUENTIAL

    def __init__(self, binary: str = "goose"):
        self.binary = binary

    def prepare(self, contract: TransitionContract, inputs: dict[str, Any]) -> dict[str, Any]:
        task = str(inputs.get("task", "")).strip()
        recipe_value = inputs.get("recipe")
        if bool(task) == bool(recipe_value):
            raise ValueError("goose.headless requires exactly one of task or recipe")

        cwd = Path(inputs.get("cwd", ".")).resolve()
        if not cwd.is_dir():
            raise ValueError(f"goose cwd does not exist: {cwd}")

        recipe = None
        if recipe_value:
            recipe = _resolve_under(cwd, str(recipe_value))
            if not recipe.is_file():
                raise ValueError(f"goose recipe does not exist: {recipe}")

        verification = inputs.get("verification")
        if not isinstance(verification, dict) or not verification.get("type"):
            raise ValueError("goose.headless requires explicit verification spec")

        timeout = float(inputs.get("timeout_seconds", 300))
        if timeout <= 0 or timeout > 3600:
            raise ValueError("timeout_seconds must be >0 and <=3600")

        return {
            "task": task or None,
            "recipe": str(recipe) if recipe else None,
            "cwd": str(cwd),
            "verification": verification,
            "timeout_seconds": timeout,
            "env": dict(inputs.get("env") or {}),
            "no_session": bool(inputs.get("no_session", True)),
        }

    def execute(self, contract: TransitionContract, prepared: dict[str, Any]) -> OperatorResult:
        binary = shutil.which(self.binary) or self.binary
        argv = [binary, "run"]
        if prepared["recipe"]:
            argv.extend(["--recipe", prepared["recipe"]])
        else:
            if prepared["no_session"]:
                argv.append("--no-session")
            argv.extend(["--with-builtin", "developer", "-t", prepared["task"]])

        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in prepared["env"].items()})
        env.setdefault("GOOSE_MODE", "auto")
        env.setdefault("GOOSE_DISABLE_SESSION_NAMING", "true")

        try:
            proc = subprocess.run(
                argv,
                cwd=prepared["cwd"],
                env=env,
                capture_output=True,
                text=True,
                timeout=prepared["timeout_seconds"],
                check=False,
            )
            result = {
                "argv": argv,
                "cwd": prepared["cwd"],
                "returncode": proc.returncode,
                "stdout": proc.stdout[-12000:],
                "stderr": proc.stderr[-12000:],
                "verification": prepared["verification"],
                "mode": "recipe" if prepared["recipe"] else "task",
            }
        except subprocess.TimeoutExpired as exc:
            result = {
                "argv": argv,
                "cwd": prepared["cwd"],
                "timed_out": True,
                "timeout_seconds": prepared["timeout_seconds"],
                "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
                "stderr": (exc.stderr or "")[-12000:] if isinstance(exc.stderr, str) else "",
                "verification": prepared["verification"],
                "mode": "recipe" if prepared["recipe"] else "task",
            }

        # A timeout or non-zero return does not prove no side effect occurred.
        return OperatorResult(result=result, side_effect_possible=True)

    def verify(self, contract: TransitionContract, execution: OperatorResult) -> VerificationResult:
        spec = execution.result["verification"]
        verification = verify_spec(spec, cwd=execution.result["cwd"])
        metadata = dict(verification.metadata)
        metadata.update(
            {
                "executor": "goose.headless",
                "goose_mode": execution.result.get("mode"),
                "goose_returncode": execution.result.get("returncode"),
                "goose_timed_out": bool(execution.result.get("timed_out", False)),
            }
        )
        return VerificationResult(
            verified=verification.verified,
            observation=verification.observation,
            source_locator=verification.source_locator,
            metadata=metadata,
        )


def _resolve_under(root: Path, value: str) -> Path:
    path = Path(value)
    candidate = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"goose recipe escapes configured cwd: {candidate}") from exc
    return candidate
