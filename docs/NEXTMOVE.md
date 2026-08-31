# Logistinfra `/next` — executable wedge

`/next` exposes one dependency-correct transition at a time.

## Invariants

1. Candidate actions are ineligible unless prerequisites are met, authority is available, and an observable receipt exists.
2. Selection is lexicographic: external consequence → information gain → technical ownership → warm access → compounding leverage → less internal preparation.
3. `EXECUTED` is never treated as `VERIFIED` merely because an action was attempted.
4. A `RECEIPT`, `CAPABILITY_GAIN`, or `FALSIFIED_HYPOTHESIS` settlement requires an inspectable receipt locator.
5. Timer expiry does not auto-complete anything; it changes the operator state to `EXPIRED_NEEDS_SETTLEMENT`.
6. Mission history is append-only. Settlement is terminal.

## CLI surface

After installing the package:

```bash
ro next-start --spec examples/next_market.json
ro next
ro serve --host 127.0.0.1 --port 8787
```

Open `http://127.0.0.1:8787/next`.

Settle from the page or CLI:

```bash
ro next-settle RECEIPT \
  --observation "Proposal submitted and visible in Freelancer" \
  --receipt "https://..." \
  --next-action "Wait for buyer response; do not rebid blindly"
```

## HTTP surface

- `GET /next` — minimal operator screen
- `GET /api/next` — current transition JSON
- `POST /api/mission` — start mission from the same JSON structure as the example
- `POST /api/settle/{mission_id}` — settle with `outcome`, `observation`, optional `receipt_locator`, optional `next_action`
- `GET /api/events/{mission_id}` — append-only mission event history

The UI is intentionally not a dashboard. It shows TARGET, NOW, DELTA, one NEXT MOVE, timer, expected receipt, urgency, and settlement controls.
