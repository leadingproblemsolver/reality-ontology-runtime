# Leverage Firewall — Structuralized Child Contract

Priority: P0
Parent: `operational-reality-v1`

## PURPOSE
Prevent <=1x non-essential human labour from consuming the user's day. Necessary low-leverage work is compressed to a reliable floor rather than ignored.

## INVOKE_WHEN
- a transition would enter the user's active queue;
- recurring labour is detected;
- the same manual action appears twice;
- new maintenance/admin/tracking work appears;
- a tool/integration can replace human labour.

## INPUTS
For each labour item:
- trigger/frequency;
- mandatory/protective/relationship-critical status;
- human minutes per occurrence;
- future occurrences;
- available connected tools/products/OSS;
- setup/integration cost;
- recurring maintenance cost;
- unique human judgment/access requirement;
- downstream unlock/evidence value.

## CLASSIFICATION
`KILL | AUTOMATE | DELEGATE | BATCH | FLOOR | KEEP`

### KILL
Optional, non-compounding, non-protective, <=1x labour.

### AUTOMATE
Stable trigger + bounded inputs + reliable tool-executable output.

### DELEGATE
Necessary but user-specific judgment is unnecessary.

### BATCH
Necessary repeated work dominated by setup/switching cost.

### FLOOR
Mandatory/protective/relationship-critical but low leverage.
Do minimum reliable version and pre-stage it.

### KEEP
Human uniquely supplies judgment, trust, negotiation, access, learning bottleneck removal, or high external consequence.

## TOOL RESOLUTION ORDER
1. existing connected tool;
2. existing product;
3. existing OSS;
4. reusable repo component;
5. thin adapter;
6. custom only if acceptance proves necessary.

## OUTPUT
```yaml
labour_decision:
  item:
  disposition:
  reason:
  mandatory_exception:
  human_minutes_now:
  recurring_minutes:
  existing_executor:
  integration_cost:
  maintenance_cost:
  floor_or_kill_rule:
  trigger:
  evidence:
```

## MVE
Run the firewall over current active workstreams plus recurring categories:
- manual tracking;
- inbox checking;
- site navigation/setup;
- university/admin compliance;
- getting-ready routines;
- repeated context assembly.

Do not attempt life-wide classification in V1.

## ACCEPTANCE
- <=1x optional work cannot enter CogniTimeExec;
- observable state is not manually tracked twice;
- repeatable necessary work is routed to tool/batch/floor;
- mandatory obligations retain reliable completion;
- every automation has lower expected maintenance than labour removed.

## FAILURE
If leverage cannot be estimated:
classify as `MEASURE_ONCE`, capture real duration/frequency, then re-evaluate. Do not build automation from guesses.

## AUTHORITY
The firewall controls labour allocation, not the intrinsic worth of people/relationships. Interactions are classified only by obligation, consequence, trust, access and state change.

## FIRST RECEIPT
At least one recurring manual operation is removed or compressed, and the next occurrence requires less user labour with no missed obligation.
