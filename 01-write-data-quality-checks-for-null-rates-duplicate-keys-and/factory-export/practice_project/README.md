## Scenario

You are a Python Data Engineer reviewing a partner payment batch before warehouse publication. The Nuvepro GenAI Sandbox supplies a synthetic payment contract, staged records, and seven representative case groups. Your task is to turn that evidence into an implementation-ready data-quality specification covering null rates, duplicate business keys, staged conflicts, amount limits, adjustments, and reversals.

**Time box:** 1.5 hours. Use Microsoft 365 Copilot as a review assistant, but independently verify its suggestions against the supplied files. The sandbox does not provide authorized Python repository editing or pytest execution. Do not claim that Python, pandas, SQL, or PostgreSQL checks were implemented or executed.

Supplied materials:

- `practice_project/materials/payment_quality_cases.json`
- `practice_project/materials/sandbox_capability_statement.json`
- Learner-owned deliverable: `practice_project/payment_quality_specification.json`

After this simulation you should be able to define contract-backed quality rules, reconcile seeded outcomes, design non-sensitive failure reports, and make an evidence-based execution-readiness finding.

## Execution Steps

1. **Inspect the contract and partition.** Read the `contract` object and identify the expected batch partition, record identifier, composite business key, missing-value rules, staged-conflict statuses, amount precision, inclusive limits, and reversal behavior. Update the corresponding `partition` and `checks` fields in `practice_project/payment_quality_specification.json`. Observable result: every placeholder in those sections is replaced by a value traceable to the contract.

2. **Reconcile missing values.** Evaluate only transaction types admitted to the declared denominator. Treat nulls and strings blank after trimming as missing, while preserving structural exclusions. Complete the missing-value results for every case. Observable result: each applicable outcome records its denominator, missing count, rate, threshold, pass state, and affected record IDs.

3. **Reconcile duplicate categories.** At the declared composite-key grain, distinguish keys repeated inside the candidate batch from keys conflicting with staged records in a conflicting status. Do not fail records matching ignored staged statuses. Observable result: duplicate outcomes list keys and record IDs separately for within-batch and staged conflicts.

4. **Reconcile amounts.** Apply currency, decimal precision, inclusive payment and adjustment ranges, the zero-adjustment rule, and reversal matching against active originals. Use only contract reason codes. Observable result: each invalid amount record has one traceable reason and boundary records remain valid.

5. **Reconcile partition decisions.** Union failed record IDs across checks without duplicating identifiers. Mark a partition failed when any check fails and apply the publication rule from the capability statement. Observable result: every case has a partition, decision, publishable flag, failed-record list, and applicable check details.

6. **Define safe reporting.** Complete `failure_report` so operational users receive the identifiers needed to investigate without exposing account numbers or customer names. Search the finished specification for values from those sensitive fields and remove any occurrence.

7. **Record execution readiness.** Copy the authoritative publication and evidence statements from the capability file. Record both unavailable capabilities, mark implementation blocked, and set all executable-evidence flags accurately. Microsoft 365 Copilot may help review wording, but its output is not executable proof.

8. **Review the deliverable.** Confirm the JSON is syntactically valid and contains the six required top-level sections. Conduct a human comparison against both supplied material files and set `review_status` to `REVIEWED` only after resolving discrepancies.

## Validation

- [ ] **V1:** `artifact` identifies the required title, schema, Microsoft 365 Copilot assistance, and reviewed status.
- [ ] **V2:** `partition` matches the contract's column and expected value.
- [ ] **V3:** The null threshold is inclusive; reversals are excluded from its denominator; null and trimmed-blank references are counted.
- [ ] **V4:** Duplicate results distinguish within-batch records from active staged conflicts and ignore rejected or superseded staged records.
- [ ] **V5:** Amount results preserve two-decimal precision, USD currency, inclusive boundaries, adjustment rules, and active-original reversal matching.
- [ ] **V6:** Clean and boundary cases pass; concentrated-null, duplicate, invalid-amount, and mixed-defect cases reconcile to their planted records.
- [ ] **V7:** No `account_number`, `customer_name`, or corresponding sensitive value appears in the completed specification.
- [ ] **V8:** Every failed partition has `publishable` set to false.
- [ ] **V9:** Readiness is `BLOCKED`; both unavailable capabilities are named; Python editing, pytest execution, and executable proof are false.
- [ ] **V10:** A browser JSON validator accepts `practice_project/payment_quality_specification.json`. This validates syntax only and must not be described as pytest or executable implementation evidence.

If validation fails, return to the execution step covering the affected check and trace each record directly against the contract. No setup or teardown is required because the browser workspace creates no external or cost-bearing resources.

## Grading

1. **Contract-backed check definitions — 25 points.** Are all null, duplicate, staged-conflict, amount, adjustment, and reversal rules complete and traceable to the supplied contract?
2. **Outcome reconciliation — 30 points.** Do all seven case groups contain accurate counts, rates, keys, violations, decisions, and failed record IDs?
3. **Failure-report safety — 15 points.** Are required operational identifiers present while sensitive fields and values are prohibited?
4. **Publication and readiness finding — 20 points.** Does the specification prevent failed-partition publication and accurately record the execution blockers and evidence limitations?
5. **Review quality — 10 points.** Is the deliverable valid JSON, internally consistent, reviewed, and free of unsupported execution claims?

Grade bands: A = 90–100, B = 80–89, C = 70–79, D = 60–69, F = below 60. The pass mark is 70. Contract definitions, case reconciliation, safe reporting, and readiness are independently scorable for partial credit.