# Goose execution integration

Reality Ontology does **not** implement another general-purpose agent loop. V1 delegates real local engineering execution to [goose](https://github.com/aaif-goose/goose) and keeps this repository responsible for policy, evidence, verification, settlement, and recovery semantics.

## Boundary

```text
TransitionContract
  -> approval gate (Reality Ontology)
  -> GooseHeadlessOperator
  -> `goose run --no-session --with-builtin developer -t ...`
  -> shell/filesystem/code action (Goose)
  -> deterministic fresh reread (Reality Ontology)
  -> evidence
  -> event/state promotion
  -> settlement receipt
```

The adapter intentionally does **not** auto-enable arbitrary MCP extensions yet. Goose with its `developer` builtin can perform broad local actions, so the operator is conservatively classified as `L2_EXTERNAL_CONSEQUENTIAL` and requires approval.

## Install Goose

Follow Goose's official installation instructions. The adapter expects a `goose` executable on `PATH`, or a caller may instantiate `GooseHeadlessOperator(binary="/absolute/path/to/goose")`.

## Minimal use

```python
from reality_ontology.models import RiskLevel, TransitionContract
from reality_ontology.operators import GooseHeadlessOperator

operator = GooseHeadlessOperator()

inputs = {
    "task": "Create docs/runtime-smoke.txt containing REALITY_EXECUTED and run the relevant tests.",
    "cwd": "/path/to/workspace",
    "verification": {
        "type": "file_contains",
        "path": "docs/runtime-smoke.txt",
        "contains": "REALITY_EXECUTED",
    },
}
```

Supported deterministic V1 verification specs:

- `path_exists`
- `file_contains`
- `command_exit`

The tool's own stdout, exit code, or success prose are receipts about execution, **not proof of the desired external state**.

## Hostile boundary already covered

The adapter test deliberately uses an executor that performs a side effect and then times out. Reality Ontology still performs the fresh reread and can establish that the effect happened. This is the first executable form of:

```text
execution may have happened
-> local executor did not return cleanly
-> do not infer failure from missing success
-> reread reality
-> verify observed state
```

## Next integration gate

After the local Goose adapter is green, add exactly one Goose MCP extension behind the same approval/verification boundary and test an externally reversible mutation. Do not add LangGraph, Hatchet, browser-use, or a memory framework until an observed workflow proves Goose + the Reality layer cannot cover the requirement cleanly.
