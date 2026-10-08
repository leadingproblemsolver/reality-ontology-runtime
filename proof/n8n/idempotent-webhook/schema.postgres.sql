-- Retry-safe webhook state contract for Postgres.
-- The event_key MUST come from the provider/business event identity when available.
-- Do not use n8n's execution id as the business idempotency key.

CREATE TABLE IF NOT EXISTS webhook_event_guard (
    event_key text PRIMARY KEY,
    state text NOT NULL CHECK (state IN ('PROCESSING','COMPLETED','FAILED')),
    attempt_count integer NOT NULL DEFAULT 1,
    receipt jsonb,
    last_error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- Atomic first claim.
-- Exactly one concurrent delivery can insert this event_key.
INSERT INTO webhook_event_guard(event_key, state)
VALUES ($1, 'PROCESSING')
ON CONFLICT (event_key) DO NOTHING
RETURNING event_key, state, attempt_count;

-- Inspect after a conflict:
SELECT event_key, state, attempt_count, receipt, last_error
FROM webhook_event_guard
WHERE event_key = $1;

-- On successful external side effect, persist the externally inspectable receipt.
UPDATE webhook_event_guard
SET state='COMPLETED',
    receipt=$2::jsonb,
    last_error=NULL,
    updated_at=now()
WHERE event_key=$1
  AND state='PROCESSING';

-- On failure before a verified receipt:
UPDATE webhook_event_guard
SET state='FAILED',
    last_error=$2,
    updated_at=now()
WHERE event_key=$1
  AND state='PROCESSING';

-- Retry a known failed event without inventing a new event identity.
UPDATE webhook_event_guard
SET state='PROCESSING',
    attempt_count=attempt_count+1,
    last_error=NULL,
    updated_at=now()
WHERE event_key=$1
  AND state='FAILED'
RETURNING event_key, state, attempt_count;
