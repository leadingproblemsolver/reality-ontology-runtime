from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .models import VerificationResult


def verify_spec(spec: dict[str, Any], *, cwd: str | Path) -> VerificationResult:
    """Deterministically verify an observed postcondition from fresh state.

    Supported V1 verification types are deliberately small and inspectable:
    - path_exists
    - file_contains
    - command_exit

    The verifier never trusts the executor's success string as proof.
    """
    kind = spec.get("type")
    root = Path(cwd).resolve()

    if kind == "path_exists":
        target = _resolve_under(root, spec["path"])
        ok = target.exists()
        return VerificationResult(
            verified=ok,
            observation=f"fresh reread: path {'exists' if ok else 'missing'}: {target}",
            source_locator=str(target),
            metadata={"type": kind, "path": str(target)},
        )

    if kind == "file_contains":
        target = _resolve_under(root, spec["path"])
        expected = str(spec["contains"])
        text = target.read_text(encoding="utf-8") if target.is_file() else ""
        ok = expected in text
        return VerificationResult(
            verified=ok,
            observation=(
                f"fresh reread: expected content {'found' if ok else 'not found'} "
                f"in {target}"
            ),
            source_locator=str(target),
            metadata={"type": kind, "path": str(target), "expected": expected},
        )

    if kind == "command_exit":
        argv = spec.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            raise ValueError("command_exit verification requires non-empty string argv list")
        expected = int(spec.get("exit_code", 0))
        timeout = float(spec.get("timeout_seconds", 60))
        proc = subprocess.run(
            argv,
            cwd=root,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        ok = proc.returncode == expected
        return VerificationResult(
            verified=ok,
            observation=f"fresh command verification exit={proc.returncode}, expected={expected}",
            source_locator=f"command://{' '.join(argv)}",
            metadata={
                "type": kind,
                "argv": argv,
                "returncode": proc.returncode,
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
            },
        )

    raise ValueError(f"unsupported verification type: {kind!r}")


def _resolve_under(root: Path, value: str) -> Path:
    path = Path(value)
    candidate = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"verification path escapes configured cwd: {candidate}") from exc
    return candidate
