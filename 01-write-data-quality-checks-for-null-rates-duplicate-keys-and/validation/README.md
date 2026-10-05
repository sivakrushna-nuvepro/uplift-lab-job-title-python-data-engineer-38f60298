# Offline Validation and Reporting Instructions

## Scenario

This directory supports offline Factory validation of the reviewed payment-quality specification. The validation seat receives the frozen pytest tests and synthetic fixtures separately from learner-facing simulation materials. The simulated Nuvepro GenAI Sandbox still lacks authorized Python repository editing and pytest execution. Running Factory validation does not change that readiness finding.

The validation process uses only local files. It requires no credentials, network access, PostgreSQL connection, cloud storage, or external publisher.

## Execution Steps

1. Start in the repository root.
2. Confirm that the Factory test seat has supplied the frozen tests and fixtures under `validation/`.
3. Confirm that the reviewed artifact exists at `reference_project/payment_quality_specification.json`.
4. Run the exact validation command:

   ```text
   python -m pytest -q
   ```

5. Read the terminal result. A valid reference artifact produces a successful pytest exit code.
6. Inspect the generated local report at `validation/report.json`.

The pytest support plugin in `validation/conftest.py` writes the report atomically at session completion. It replaces a previous local report rather than appending to it.

## Validation

Check each item:

- [ ] The command used was exactly `python -m pytest -q`.
- [ ] Pytest completed with exit code 0.
- [ ] `validation/report.json` was generated after the test run.
- [ ] The report has `schemaVersion` equal to `factory-validation-report.v1`.
- [ ] The report has `command` equal to `python -m pytest -q`.
- [ ] The report has `exitCode` equal to 0 and `decision` equal to `PASSED`.
- [ ] The report contains deterministic integer counts for collected, passed, failed, skipped, and error outcomes.
- [ ] No external publication was attempted.

If pytest reports that tests, fixtures, or the reference specification are absent, the Factory test seat is incomplete. Restore the supplied package files rather than weakening, skipping, or editing the frozen tests.

If the report is absent after pytest finishes, confirm that `validation/conftest.py` is present and that pytest discovered the `validation` test tree. Do not create a hand-written report because it would not be execution evidence.

## Grading

Factory verification uses the frozen pytest suite as the objective pass/fail signal. Graders use `validation/grading_rubric.md` for the separate 100-point review of contract interpretation, reconciled outcomes, privacy-safe reporting, publication safety, and readiness honesty.

The generated report is local evidence only. No S3 publisher or other network publisher is enabled or required. Offline verification must not upload the specification, fixtures, test output, or report. A failed partition remains non-publishable regardless of whether the validation tooling itself ran successfully.