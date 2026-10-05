import json
from pathlib import Path

import pytest


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "payment_quality_cases.json"
CAPABILITY_PATH = (
    Path(__file__).parent / "fixtures" / "sandbox_capability_statement.json"
)
SPECIFICATION_PATH = (
    Path(__file__).parents[1]
    / "reference_project"
    / "payment_quality_specification.json"
)


@pytest.fixture(scope="module")
def fixture_data():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def contract(fixture_data):
    return fixture_data["contract"]


@pytest.fixture(scope="module")
def capability_statement():
    return json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def specification():
    assert SPECIFICATION_PATH.is_file(), (
        "Create the reviewed implementation specification at "
        "reference_project/payment_quality_specification.json"
    )
    return json.loads(SPECIFICATION_PATH.read_text(encoding="utf-8"))


def assert_ids(actual, expected):
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def assert_violations(actual, expected):
    normalized_actual = {
        (violation["record_id"], violation["reason"]) for violation in actual
    }
    normalized_expected = {
        (violation["record_id"], violation["reason"]) for violation in expected
    }
    assert len(actual) == len(expected)
    assert normalized_actual == normalized_expected


def test_artifact_is_a_reviewed_copilot_assisted_specification(specification):
    assert specification["artifact"] == {
        "title": "Write data-quality checks for null rates, duplicate keys, and out-of-range amounts.",
        "kind": "DATA_QUALITY_IMPLEMENTATION_SPECIFICATION",
        "schema_version": "payment-quality-specification.v1",
        "assistance": "Microsoft 365 Copilot",
        "review_status": "REVIEWED",
    }
    assert specification["partition"] == {
        "column": "batch_date",
        "expected_value": "2025-02-14",
    }


def test_specification_defines_missing_value_rate_contract(
    specification, contract
):
    definition = specification["checks"]["missing_values"]
    source = contract["missing_value_check"]

    assert definition == {
        "field": source["field"],
        "denominator_transaction_types": source[
            "denominator_transaction_types"
        ],
        "blank_after_trimming_is_missing": True,
        "maximum_rate": pytest.approx(0.2),
        "threshold_is_inclusive": True,
        "calculation": "missing_count / denominator",
        "structural_exclusions": ["REVERSAL"],
    }


def test_specification_defines_duplicate_key_and_staged_conflict_contract(
    specification, contract
):
    definition = specification["checks"]["duplicate_keys"]

    assert definition == {
        "key_columns": contract["business_key"],
        "within_batch_rule": "MORE_THAN_ONE_RECORD_WITH_THE_SAME_COMPOSITE_KEY",
        "staged_conflict_rule": "COMPOSITE_KEY_MATCHES_A_CONFLICTING_STAGED_RECORD",
        "staged_partition_column": "batch_date",
        "conflicting_staged_statuses": ["ACTIVE"],
        "ignored_staged_statuses": ["REJECTED", "SUPERSEDED"],
        "within_batch_and_staged_conflicts_reported_separately": True,
    }


def test_specification_defines_amount_and_reversal_contract(
    specification, contract
):
    definition = specification["checks"]["amounts"]
    source = contract["amount_check"]

    assert definition == {
        "currency": source["currency"],
        "precision": source["precision"],
        "payment_minimum": source["payment_minimum"],
        "payment_maximum": source["payment_maximum"],
        "boundaries_are_inclusive": True,
        "adjustment_minimum": source["adjustment_minimum"],
        "adjustment_maximum": source["adjustment_maximum"],
        "zero_adjustment_allowed": False,
        "reversal_requires_active_original": True,
        "reversal_must_equal_negative_original_amount": True,
        "reason_codes": source["reason_codes"],
    }


def test_clean_and_boundary_records_are_reconciled(specification):
    outcomes = specification["expected_outcomes"]

    clean = outcomes["clean"]
    assert clean["partition"] == {"batch_date": "2025-02-14"}
    assert clean["decision"] == "PASSED"
    assert clean["publishable"] is True
    assert clean["failed_record_ids"] == []
    assert clean["checks"] == {
        "missing_values": {
            "denominator": 2,
            "missing_count": 0,
            "rate": 0.0,
            "failed_record_ids": [],
        },
        "duplicate_keys": {
            "within_batch_record_ids": [],
            "staged_conflict_record_ids": [],
        },
        "amounts": {"failed_record_ids": [], "violations": []},
    }

    for case_name in ("null_threshold_boundary", "amount_boundaries"):
        assert outcomes[case_name]["partition"] == {
            "batch_date": "2025-02-14"
        }
        assert outcomes[case_name]["decision"] == "PASSED"
        assert outcomes[case_name]["publishable"] is True
        assert outcomes[case_name]["failed_record_ids"] == []

    threshold = outcomes["null_threshold_boundary"]["checks"][
        "missing_values"
    ]
    assert threshold["denominator"] == 5
    assert threshold["missing_count"] == 1
    assert threshold["rate"] == pytest.approx(0.2)
    assert threshold["threshold"] == pytest.approx(0.2)
    assert threshold["passed"] is True


def test_concentrated_null_outcome_uses_declared_denominator_and_blanks(
    specification
):
    outcome = specification["expected_outcomes"]["concentrated_nulls"]
    check = outcome["checks"]["missing_values"]

    assert outcome["partition"] == {"batch_date": "2025-02-14"}
    assert outcome["decision"] == "FAILED"
    assert outcome["publishable"] is False
    assert check["denominator"] == 5
    assert check["missing_count"] == 2
    assert check["rate"] == pytest.approx(0.4)
    assert check["threshold"] == pytest.approx(0.2)
    assert check["passed"] is False
    assert_ids(check["failed_record_ids"], ["N-002", "N-004"])
    assert "N-006" not in check["failed_record_ids"]


def test_duplicate_outcome_distinguishes_conflict_categories(specification):
    outcome = specification["expected_outcomes"]["duplicates"]
    check = outcome["checks"]["duplicate_keys"]

    assert outcome["decision"] == "FAILED"
    assert outcome["publishable"] is False
    assert check["within_batch_keys"] == [
        {"partner_id": "PARTNER-A", "payment_id": "DUP-100"}
    ]
    assert check["staged_conflict_keys"] == [
        {"partner_id": "PARTNER-B", "payment_id": "STAGED-900"}
    ]
    assert_ids(check["within_batch_record_ids"], ["D-001", "D-002"])
    assert_ids(check["staged_conflict_record_ids"], ["D-003"])
    assert_ids(outcome["failed_record_ids"], ["D-001", "D-002", "D-003"])
    assert "D-004" not in outcome["failed_record_ids"]


def test_invalid_amount_outcomes_reconcile_every_reason_code(specification):
    outcome = specification["expected_outcomes"]["invalid_amounts"]
    check = outcome["checks"]["amounts"]
    expected = [
        {"record_id": "A-001", "reason": "OUT_OF_RANGE"},
        {"record_id": "A-002", "reason": "OUT_OF_RANGE"},
        {"record_id": "A-003", "reason": "INVALID_PRECISION"},
        {"record_id": "A-004", "reason": "CURRENCY_MISMATCH"},
        {"record_id": "A-005", "reason": "ZERO_ADJUSTMENT"},
        {"record_id": "A-006", "reason": "REVERSAL_MISMATCH"},
    ]

    assert outcome["decision"] == "FAILED"
    assert outcome["publishable"] is False
    assert_ids(check["failed_record_ids"], [item["record_id"] for item in expected])
    assert_violations(check["violations"], expected)


def test_mixed_defects_are_reconciled_without_sensitive_values(
    specification, fixture_data
):
    outcome = specification["expected_outcomes"]["mixed_defects"]

    missing = outcome["checks"]["missing_values"]
    assert missing["denominator"] == 5
    assert missing["missing_count"] == 2
    assert missing["rate"] == pytest.approx(0.4)
    assert_ids(missing["failed_record_ids"], ["M-003", "M-005"])

    duplicates = outcome["checks"]["duplicate_keys"]
    assert duplicates["within_batch_keys"] == [
        {"partner_id": "PARTNER-M", "payment_id": "MIX-DUP"}
    ]
    assert_ids(duplicates["within_batch_record_ids"], ["M-001", "M-002"])

    amounts = outcome["checks"]["amounts"]
    assert_violations(
        amounts["violations"],
        [{"record_id": "M-004", "reason": "OUT_OF_RANGE"}],
    )
    assert_ids(
        outcome["failed_record_ids"],
        ["M-001", "M-002", "M-003", "M-004", "M-005"],
    )
    assert outcome["decision"] == "FAILED"
    assert outcome["publishable"] is False

    serialized = json.dumps(specification, sort_keys=True)
    for record in fixture_data["cases"]["mixed_defects"]:
        assert record["account_number"] not in serialized
        assert record["customer_name"] not in serialized


def test_failure_report_fields_are_implementation_ready(specification):
    assert specification["failure_report"] == {
        "required_top_level_fields": [
            "partition",
            "decision",
            "publishable",
            "failed_record_ids",
            "checks",
        ],
        "non_sensitive_identifier_fields": [
            "record_id",
            "partner_id",
            "payment_id",
        ],
        "prohibited_sensitive_fields": [
            "account_number",
            "customer_name",
        ],
        "missing_value_failure_fields": ["record_id", "field"],
        "duplicate_failure_fields": [
            "record_id",
            "partner_id",
            "payment_id",
            "conflict_type",
        ],
        "amount_failure_fields": ["record_id", "reason"],
    }


def test_readiness_finding_records_publication_and_execution_blockers(
    specification, capability_statement
):
    readiness = specification["readiness_finding"]

    assert readiness["publication_rule"] == capability_statement[
        "required_publication_rule"
    ]
    assert readiness["implementation_status"] == "BLOCKED"
    assert readiness["blocking_observation"] == capability_statement[
        "blocking_observation"
    ]
    assert set(readiness["unavailable_capabilities"]) == {
        "AUTHORIZED_PYTHON_REPOSITORY_EDITING",
        "PYTEST_EXECUTION",
    }
    assert set(readiness["completion_requires"]) == {
        "AUTHORIZED_PYTHON_REPOSITORY_EDITING",
        "PYTEST_EXECUTION",
    }
    assert readiness["copilot_evidence_rule"] == capability_statement[
        "copilot_evidence_rule"
    ]
    assert readiness["python_repository_edited"] is False
    assert readiness["pytest_executed"] is False
    assert readiness["executable_proof"] is False