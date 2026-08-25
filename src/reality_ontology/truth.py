from __future__ import annotations
from .models import TruthState, TRUTH_ORDER

_INDEX = {state.value: i for i, state in enumerate(TRUTH_ORDER)}

class TruthPromotionError(ValueError):
    pass

def ensure_promotion_allowed(current: str | None, desired: str, evidence_types: set[str]) -> None:
    if desired not in _INDEX:
        return  # domain state outside the universal proof ladder
    if current in _INDEX and _INDEX[desired] < _INDEX[current]:
        raise TruthPromotionError(f"truth-state regression requires an explicit corrective event: {current} -> {desired}")

    required = {
        TruthState.TESTED.value: {"test_result"},
        TruthState.DEPLOYED.value: {"deployment_receipt"},
        TruthState.EXPOSED.value: {"external_receipt"},
        TruthState.EXTERNALLY_USED.value: {"external_use_receipt"},
        TruthState.REUSED.value: {"reuse_receipt"},
        TruthState.ADOPTED.value: {"adoption_receipt"},
        TruthState.PAID.value: {"payment_receipt"},
        TruthState.OUTCOME_PRODUCING.value: {"outcome_measurement"},
    }
    needed = required.get(desired)
    if needed and not (needed & evidence_types):
        raise TruthPromotionError(
            f"cannot promote to {desired}; requires evidence type one of {sorted(needed)}"
        )
