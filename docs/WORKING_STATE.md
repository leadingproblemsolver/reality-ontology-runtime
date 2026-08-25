# Working State — V0

## Proven locally and in CI

- SQLite durable Reality Store initializes from an empty path.
- Evidence must exist before an event can reference it.
- Current object state is reconstructed from event history.
- Universal truth ladder blocks unsupported `DEPLOYED` promotion.
- L2 external/consequential operators are blocked without explicit approval.
- Execute and verify are separate stages.
- Successful verified runs persist an evidence receipt, event, settlement receipt, and `SETTLED` attempt.
- Fresh `RealityStore` process reconstructs the final state and context.
- Strong contradictory reality signals invalidate dependent decisions and remove them from active context.
- Canonical relations require evidence provenance.
- Re-running an already settled demo transition becomes a no-op rather than repeating the side effect.
- Standard CI is green on the publication branch.

## Proven against a real external system

GitHub Actions run `32861760131` executed the actual Goose CLI `1.47.0`, a real MCP stdio server, and a reversible GitHub issue mutation using the workflow-scoped `GITHUB_TOKEN`.

Two independently verified paths passed:

1. **Normal path**
   - marker: `reality-goose-mcp-32861760131-1-normal`
   - GitHub issue: `#7`
   - Goose returned normally (`goose_timed_out=false`).
   - Reality independently reread GitHub, verified the uniquely correlated external issue, recorded evidence `ev_4475c9712e544686`, settled as `settlement_0d9e9a9fe5164216`, and a fresh process reconstructed state `EXPOSED`.

2. **Ambiguous external-effect path**
   - marker: `reality-goose-mcp-32861760131-1-ambiguous`
   - GitHub issue: `#8`
   - the MCP tool created the external issue and persisted its transport receipt, then deliberately stalled before returning;
   - Goose was terminated by the caller timeout (`goose_timed_out=true`);
   - Reality did **not** replay the external mutation;
   - Reality independently reread GitHub, reconciled the one matching external effect, recorded evidence `ev_8c463cb358a44de5`, settled as `settlement_ab70970e09614b12`, and a fresh process reconstructed state `EXPOSED`.

Both probe issues were then closed by the workflow cleanup. The run retained the Reality databases, transport receipts, and provider log as Actions artifact `9568459773` (`goose-mcp-settlement-32861760131`).

This proves the concrete invariant:

`external effect may have occurred -> caller does not receive success -> reread external truth -> do not duplicate mutation -> record evidence -> settle -> recover after restart`

The verification path also uses bounded polling for read-side propagation lag; it never retries the write merely because a collection read has not converged yet.

## Not yet claimed

- No first-class Gmail/browser/CRM operator is implemented in the core runtime.
- The GitHub proof is currently exercised through the Goose + MCP integration harness rather than a dedicated core GitHub operator.
- No production database migration framework.
- No concurrent/distributed-worker locking proof.
- No arbitrary host/process crash proof beyond the controlled caller-timeout-after-external-effect case above.
- No production-scale benchmark or load evidence.
- No claim about LLM planning quality; the external smoke intentionally uses a deterministic local OpenAI-compatible provider so tool registration/execution is reproducible while the Goose process and MCP/GitHub side effects remain real.

## Next evidence event

Do **not** add another agent runtime by default. Reuse this settlement substrate in one independent live developer stack where the same ambiguity is already a real problem (for example LangGraph or PydanticAI), and prove the same external-effect reconciliation invariant there. A second independent stack is now more informative than more internal architecture.
