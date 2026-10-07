from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "proof" / "n8n" / "idempotent-webhook" / "idempotent_webhook.py"
spec = importlib.util.spec_from_file_location("idempotent_webhook", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

IdempotentWebhookStore = module.IdempotentWebhookStore
process_delivery = module.process_delivery


def test_same_event_delivered_repeatedly_causes_one_side_effect(tmp_path):
    store = IdempotentWebhookStore(tmp_path / "events.db")
    calls = []

    def side_effect():
        calls.append("sent")
        return "message:123"

    first = process_delivery(store, "evt-1", side_effect)
    second = process_delivery(store, "evt-1", side_effect)
    third = process_delivery(store, "evt-1", side_effect)

    assert first.state == "COMPLETED"
    assert second.decision == "RETURN_EXISTING_RECEIPT"
    assert third.decision == "RETURN_EXISTING_RECEIPT"
    assert calls == ["sent"]
    assert store.get("evt-1")["receipt"] == "message:123"
    store.close()


def test_failed_attempt_is_retryable_without_changing_event_identity(tmp_path):
    store = IdempotentWebhookStore(tmp_path / "events.db")
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary downstream failure")
        return "order:456"

    try:
        process_delivery(store, "evt-2", flaky)
    except RuntimeError:
        pass

    failed = store.get("evt-2")
    assert failed["state"] == "FAILED"
    assert failed["attempt_count"] == 1

    retried = process_delivery(store, "evt-2", flaky)
    assert retried.state == "COMPLETED"
    assert retried.attempt_count == 2
    assert retried.receipt == "order:456"
    store.close()


def test_inflight_duplicate_is_suppressed(tmp_path):
    store = IdempotentWebhookStore(tmp_path / "events.db")
    first = store.claim("evt-3")
    duplicate = store.claim("evt-3")

    assert first.decision == "EXECUTE"
    assert duplicate.decision == "SUPPRESS_DUPLICATE_IN_FLIGHT"
    store.close()


def test_concurrent_claims_have_exactly_one_executor(tmp_path):
    db_path = tmp_path / "events.db"
    bootstrap = IdempotentWebhookStore(db_path)
    bootstrap.close()

    barrier = threading.Barrier(8)
    results = []
    lock = threading.Lock()

    def worker():
        local = IdempotentWebhookStore(db_path)
        barrier.wait()
        result = local.claim("evt-concurrent")
        with lock:
            results.append(result.decision)
        local.close()

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count("EXECUTE") == 1
    assert results.count("SUPPRESS_DUPLICATE_IN_FLIGHT") == 7
