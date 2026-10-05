# Data-Quality Specification Grading Rubric and Reference Key

> Grader-only material. Do not provide this file to learners during the simulation.

## Assessment scope

Score the reviewed payment-quality implementation specification against the supplied contract, representative records, and sandbox capability statement. The file `reference_project/payment_quality_specification.json` is one valid reviewed answer. It is not the only acceptable wording or document layout, provided the candidate preserves every contract rule and reconciles every expected result.

The frozen pytest suite is the objective pass/fail signal for the packaged reference artifact. Run:

```text
python -m pytest -q
```

The support plugin generates `validation/report.json` after the run. That report is local validation evidence, not an input file and not evidence of external publication.

## Scored rubric: 100 points

### 1. Missing-value contract and reasoning: 20 points

- **18-20:** Defines `payer_reference` as the checked field. Uses only PAYMENT and ADJUSTMENT records in the denominator. Treats null and blank-after-trimming values as missing. Excludes REVERSAL structural nulls. Calculates `missing_count / denominator`. Correctly treats the maximum rate of 0.2 as inclusive.
- **13-17:** Correct denominator and threshold decision, with one minor omission in terminology or structural-null explanation.
- **7-12:** Identifies null-rate checking but uses an incomplete denominator, omits blank semantics, or leaves threshold inclusivity ambiguous.
- **1-6:** Mentions nulls without an implementation-ready calculation.
- **0:** Missing or contradicts the contract.

Reference reconciliation:

- Clean: denominator 2, missing 0, rate 0.0, pass.
- Threshold boundary: denominator 5, missing 1, rate 0.2, pass.
- Concentrated nulls: denominator 5, missing 2, rate 0.4, fail records N-002 and N-004. N-006 is structurally excluded.
- Mixed defects: denominator 5, missing 2, rate 0.4, fail records M-003 and M-005.

### 2. Duplicate-key and staged-conflict contract: 20 points

- **18-20:** Uses the composite key `(partner_id, payment_id)`. Defines more than one same-key record as a within-batch conflict. Separately identifies matching ACTIVE staged records. Uses `batch_date` as the staged partition column. Explicitly ignores REJECTED and SUPERSEDED staged records.
- **13-17:** Correct key and conflict results, with one minor omission in staged-state documentation.
- **7-12:** Detects within-batch duplicates but merges staged conflicts into the same category or mishandles ignored statuses.
- **1-6:** Uses a partial key or gives only a generic uniqueness statement.
- **0:** Missing or materially incorrect.

Reference reconciliation:

- Duplicate case within-batch key: PARTNER-A and DUP-100, records D-001 and D-002.
- Duplicate case staged conflict key: PARTNER-B and STAGED-900, record D-003.
- D-004 does not fail because its staged match is REJECTED.
- Mixed case within-batch key: PARTNER-M and MIX-DUP, records M-001 and M-002.

### 3. Amount, currency, precision, and reversal rules: 20 points

- **18-20:** Requires USD and precision 2. Uses inclusive payment bounds 0.01 through 10000.00 and inclusive adjustment bounds -10000.00 through 10000.00. Rejects zero adjustments. Requires an ACTIVE original for reversals and requires the reversal amount to equal the negative original amount. Uses only the documented reason codes.
- **13-17:** Correct outcomes with one minor omission in the written boundary or reversal explanation.
- **7-12:** Handles ordinary ranges but omits precision, currency, zero adjustments, or active-original reversal semantics.
- **1-6:** Provides only a generic numeric range check.
- **0:** Missing or materially contradicts the contract.

Reference reconciliation:

- All amount-boundary records pass, including inclusive minimum and maximum values and the valid reversal.
- A-001 and A-002: OUT_OF_RANGE.
- A-003: INVALID_PRECISION.
- A-004: CURRENCY_MISMATCH.
- A-005: ZERO_ADJUSTMENT.
- A-006: REVERSAL_MISMATCH.
- Mixed record M-004: OUT_OF_RANGE.

### 4. Complete outcome and partition reconciliation: 15 points

- **14-15:** Reconciles clean, null-threshold boundary, amount-boundary, concentrated-null, duplicate, invalid-amount, and mixed-defect cases. Every case identifies partition `batch_date=2025-02-14`, decision, publishability, failed records, and per-check details where applicable.
- **10-13:** All decisions are correct, with a small reporting omission.
- **5-9:** Most decisions are correct, but one case or several failed identifiers are missing.
- **1-4:** Provides only high-level pass/fail statements.
- **0:** No usable reconciliation.

The clean, null-threshold boundary, and amount-boundary cases pass and are publishable. Concentrated-null, duplicate, invalid-amount, and mixed-defect cases fail and are not publishable. The mixed failed-record set is M-001, M-002, M-003, M-004, and M-005.

### 5. Privacy-safe, implementation-ready failure reporting: 10 points

- **9-10:** Requires partition, decision, publishable, failed_record_ids, and checks at the top level. Permits record_id, partner_id, and payment_id as non-sensitive identifiers. Prohibits account_number and customer_name. Defines check-specific fields for missing values, duplicate conflict type, and amount reason.
- **6-8:** Safe and usable, with one minor field omission.
- **3-5:** Avoids sensitive values but does not define implementation-ready report fields.
- **1-2:** Privacy intent is stated but sensitive-field handling is ambiguous.
- **0:** Exposes or requires sensitive values.

Any occurrence of supplied account numbers or customer names in expected reports receives zero for this section and must be remediated before publication.

### 6. Publication safety and execution readiness: 15 points

- **14-15:** States that a failed partition must not be published. Marks implementation status BLOCKED. Lists authorized Python repository editing and pytest execution as both unavailable and required for completion. States that Copilot output is a reviewed specification, not executable proof. Does not claim repository editing, pytest execution, or executable proof occurred in the simulated sandbox.
- **10-13:** Correct safety decision with one minor readiness field omitted.
- **5-9:** Correctly blocks publication but overstates implementation or test evidence.
- **1-4:** Notes a limitation without a clear publication rule.
- **0:** Allows failed publication or falsely claims executable validation.

## Score bands

- **A, 90-100:** Complete, precise, privacy-safe, and implementation-ready specification.
- **B, 80-89:** Correct core decisions with limited omissions that do not change outcomes.
- **C, 70-79:** Pass. Core checks are mostly correct, but implementation details need clarification.
- **D, 60-69:** Not ready. One or more contract areas could produce an incorrect partition decision.
- **F, below 60:** Not usable as a production implementation specification.

Pass mark: **70**, subject to the critical-failure rules below.

## Critical-failure rules

A numeric score does not override these failures:

1. A failed partition is described as publishable.
2. Sensitive account numbers or customer names are included in a failure report.
3. The specification claims executable proof from Microsoft 365 Copilot.
4. The specification claims Python editing or pytest execution occurred in the simulated sandbox despite the capability statement.
5. Any of the three required check categories is absent.

## Partial-credit guidance

Score the six sections independently. A candidate can receive credit for a correct missing-value contract even if duplicate reconciliation is incomplete. Likewise, a correct privacy and publication policy receives its section credit even when an amount reason is wrong. Do not award outcome-reconciliation points merely because the final decision happens to be correct when the supporting calculation is incorrect.

Accept equivalent wording and alternate document structures. Require exact business meaning, identifiers, decisions, and reason categories rather than exact prose.

## Remediation map

| Finding | Return to | Required remediation |
|---|---|---|
| Reversal nulls counted in the denominator | Missing-value contract | Restrict the denominator to PAYMENT and ADJUSTMENT and record REVERSAL as a structural exclusion. |
| A 0.2 null rate fails | Missing-value contract | Apply the inclusive maximum threshold. |
| Blank strings pass | Missing-value contract | Trim before testing for missing values. |
| Staged and within-batch conflicts are merged | Duplicate-key contract | Report the categories independently at the composite-key grain. |
| D-004 fails | Duplicate-key contract | Ignore staged REJECTED and SUPERSEDED records. |
| Boundary amounts fail | Amount contract | Apply inclusive limits using decimal semantics. |
| Zero adjustment passes | Amount contract | Enforce the explicit zero-adjustment prohibition. |
| Reversal is checked as an ordinary adjustment | Amount contract | Resolve the ACTIVE original and compare against its exact negative amount. |
| Sensitive values appear | Failure reporting | Remove account_number and customer_name and retain only approved identifiers. |
| Failed case is publishable | Publication safety | Apply the mandatory no-publication rule to every failed partition. |
| Copilot output is called executable proof | Readiness finding | Mark implementation BLOCKED and distinguish reviewed specification evidence from execution evidence. |

## Objective validation signal

The frozen pytest suite is authoritative for the packaged reference answer. A successful run has exit code 0 and causes `validation/report.json` to contain:

- `schemaVersion` equal to `factory-validation-report.v1`
- `command` equal to `python -m pytest -q`
- `exitCode` equal to 0
- `decision` equal to `PASSED`
- deterministic collected, passed, failed, skipped, and error counts

The local report does not publish results and does not change the simulated sandbox readiness finding.