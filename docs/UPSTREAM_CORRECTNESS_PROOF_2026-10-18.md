# Upstream correctness fixes — inspectable engineering evidence

This page is an evidence index, not a claim of production ownership, customer deployment, or performance improvement. All three pull requests below were **merged** in their respective upstream repositories (verified October 18, 2026).

| Project | Public source | Failure mode | Bounded change | Evidence |
| --- | --- | --- | --- | --- |
| FlashInfer | [PR #4401](https://github.com/flashinfer-ai/flashinfer/pull/4401) | Finite masked-softmax sentinel mishandled valid extreme negative logits; fully masked rows needed explicit handling to avoid NaNs | Correct edge-case handling in attention kernels | Public merged PR description, code diff, and review history |
| MLX | [PR #4324](https://github.com/ml-explore/mlx/pull/4324) | `mx.arange` inferred `int32` even for out-of-range integer arguments, producing overflow/saturation rather than a correct range | Select `int64` when integer arguments exceed `int32` limits | Public merged PR description, code diff, and review history |
| Gymnasium | [PR #1666](https://github.com/Farama-Foundation/Gymnasium/pull/1666) | `Box.sample()` incorrectly excluded valid near-boundary values for smaller signed integer dtypes | Restrict unnecessary sampling-margin behavior while preserving necessary `int64` protection | Public merged PR description, code diff, and review history |

**Contributor identity:** The upstream commits/PRs were submitted through GitHub user [`shoutoutuoadi325`](https://github.com/shoutoutuoadi325), whereas this repository is maintained under [`leadingproblemsolver`](https://github.com/leadingproblemsolver). This index does **not** establish independently that the two accounts have the same owner. Verify public account linkage before treating these as attributable resume credentials.

## How an engineer should evaluate these

1. Open the upstream PR, read the precise issue and changed code.
2. Inspect the regression cases and the maintainer conversation, rather than accepting a summary.
3. Check the merge state and any limitations noted by maintainers.
4. Discuss the input boundary, implementation choice, and counterexamples in a technical interview.

## Separate, unfinished work

[Reality Ontology Runtime](https://github.com/leadingproblemsolver/reality-ontology-runtime) models evidence, approval, execution, verification, and settlement. Its own construction slice and ongoing runtime PRs must be assessed on their **actual respective PR states**, and its design is not proof that a real customer deployed it. Isolated Reality Handoff verifier tests found wrong-entity false-positive cases; the complete integration has **not** been verified by those isolated tests.

This page intentionally contains no synthetic benchmark numbers, job titles, or unverifiable adoption claims.
