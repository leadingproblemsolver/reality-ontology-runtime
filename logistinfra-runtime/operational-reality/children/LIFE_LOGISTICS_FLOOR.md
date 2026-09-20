# Life Logistics Floor — Structuralized Child Contract

Priority: P1
Parent: `operational-reality-v1`

## PURPOSE
Compress unavoidable recurring logistics—university, admin, getting ready, routine travel/packing/document handling—into the minimum reliable human labour.

## INVOKE_WHEN
- mandatory obligation enters horizon;
- recurring routine is due;
- new form/document/admin request arrives;
- physical preparation is required;
- user would otherwise repeatedly remember/check/assemble the same things.

## PRINCIPLE
Do not optimize away necessary life maintenance.
Create a reliable floor:

```text
detect
→ batch/default
→ pre-stage
→ one human checkpoint if necessary
→ execute
→ verify
→ disappear until next trigger
```

## V1 DOMAINS
### University
- deadline/assessment/attendance/admin obligations;
- extract from Calendar/email/source documents;
- route only assessed/required work;
- no duplicate manual deadline list.

### Getting ready
- default kits/checklists by destination/activity;
- previous-night or prior-window pre-stage;
- replenish missing recurring items through maintenance state;
- no elaborate optimization beyond measured recurring friction.

### Admin/documents
- renewal/form/payment/document requests;
- exact source + required fields + due date + submission verifier.

## OUTPUT
```yaml
floor_operation:
  obligation:
  source:
  due_window:
  minimum_definition_of_done:
  default_pack_or_template:
  pre_stage:
  human_checkpoint:
  execution_surface:
  verification:
  next_trigger:
```

## TOOLS
Use Calendar, Gmail, files, browser execution, forms, existing document templates and reminders/wake logic. No separate life-management app unless current tools cannot satisfy acceptance.

## ACCEPTANCE
- no mandatory obligation is lost;
- recurring prep uses defaults instead of reconstruction;
- duplicated tracking is removed;
- average setup/switching labour declines;
- floor operations do not crowd out primary high-leverage work.

## FAILURE
If an obligation is uncertain, surface the uncertainty once; do not create recurring manual vigilance.

## FIRST RECEIPT
One recurring university/admin/getting-ready workflow completes from detection to verification with less human setup than its previous baseline.
