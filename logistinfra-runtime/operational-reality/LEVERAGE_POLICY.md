# Daily Leverage Firewall Policy

Goal: eliminate human labour that returns <=1x time leverage unless it is mandatory, protective, or relationship-critical.

## Time leverage ratio

For recurring work:

```text
TLR =
expected future human minutes avoided or unlocked
/
(current human minutes + expected recurring maintenance minutes)
```

This is a labour filter, not a universal value metric.

## Disposition

### KILL
TLR <= 1 and the work is:
- optional;
- non-compounding;
- non-protective;
- non-commitment-bearing;
- not required for access or evidence.

### AUTOMATE
Stable trigger + bounded inputs + deterministic/reliably tool-executable output.

### DELEGATE
Necessary but human judgment need not be the user’s.

### BATCH
Necessary repeated work where setup/switching dominates execution.

### FLOOR
Mandatory/protective/relationship-critical work with TLR <= 1.
Do the minimum reliable version; standardize and pre-stage it.

Examples:
- university compliance;
- hygiene/getting ready;
- health/safety;
- required admin;
- important relationship maintenance.

### KEEP
Human action has >1x leverage or uniquely provides judgment, trust, negotiation, access, external consequence, learning bottleneck removal, or compounding proof.

## Daily gate

Before any transition enters the active human queue:

1. Can a connected tool execute it?
2. Can an existing product/OSS component execute it?
3. Can it be eliminated?
4. Can it be batched?
5. Is the user uniquely required?
6. If mandatory and <=1x, what is the floor?
7. What future labour will this remove?

## Anti-tracking rule

Never require the user to manually track state already observable from:
- calendar;
- email;
- GitHub;
- CRM;
- deployment/CI;
- payment systems;
- browser/API state.

Manual tracking is allowed only for genuinely unobservable state and must be one-touch capture.
