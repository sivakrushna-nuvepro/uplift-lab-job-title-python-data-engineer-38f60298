import json
from pathlib import Path

import pytest

from validation.test_data_quality import specification


EXPECTATION_PATH = (
    Path(__file__).parent / "fixtures" / "implementation_decision_expectation.json"
)


@pytest.fixture
def decision_expectation():
    return json.loads(EXPECTATION_PATH.read_text(encoding="utf-8"))


def test_single_implementation_decision_marks_executable_validation_blocked(
    specification, decision_expectation
):
    decision = specification["implementation_decision"]
    expected = decision_expectation["implementation_decision"]

    assert isinstance(decision, dict)
    assert decision["decision_id"] == expected["decision_id"]
    assert decision["status"] == expected["status"]
    assert decision["executable_validation"] == expected["executable_validation"]
    assert isinstance(decision["decision_basis"], str)
    assert decision["decision_basis"].strip()
    decision_basis = decision["decision_basis"].lower()
    assert "copilot" in decision_basis
    assert "does not prove" in decision_basis
    assert "passed" in decision_basis


def test_each_data_quality_check_is_recorded_as_not_executed(
    specification, decision_expectation
):
    actual = specification["implementation_decision"]["check_execution_status"]
    expected = decision_expectation["implementation_decision"][
        "check_execution_status"
    ]

    assert actual == expected
    assert set(actual) == {
        "missing_value_rate",
        "composite_key_duplicates",
        "amount_range",
    }
    assert set(actual.values()) == {"not_executed"}


def test_blocking_observation_records_both_missing_capabilities(
    specification, decision_expectation
):
    actual = specification["implementation_decision"][
        "blocking_tech_stack_observation"
    ]
    expected = decision_expectation["implementation_decision"][
        "blocking_tech_stack_observation"
    ]

    assert actual == expected
    assert actual["python_editing_authorized"] is False
    assert actual["pytest_execution_authorized"] is False


def test_failed_partition_report_contract_is_complete(
    specification, decision_expectation
):
    actual = specification["implementation_decision"]["failed_partition_report"]
    expected = decision_expectation["implementation_decision"][
        "failed_partition_report"
    ]

    assert actual["scope"] == expected["scope"]
    assert actual["emit_when"] == expected["emit_when"]
    assert actual["required_fields"] == expected["required_fields"]
    assert actual["representative_identifier_policy"] == expected[
        "representative_identifier_policy"
    ]
    assert actual["maximum_representative_identifiers"] == expected[
        "maximum_representative_identifiers"
    ]


def test_report_field_definitions_preserve_threshold_and_identifier_semantics(
    specification, decision_expectation
):
    actual = specification["implementation_decision"]["failed_partition_report"][
        "field_definitions"
    ]
    expected = decision_expectation["implementation_decision"][
        "failed_partition_report"
    ]["field_definitions"]

    assert actual == expected
    assert actual["affected_count"]["type"] == "integer"
    assert actual["affected_count"]["minimum"] == 1
    assert actual["threshold_or_limit"]["type"] == "string"
    assert actual["representative_record_ids"]["type"] == "array"
    assert actual["representative_record_ids"]["items"] == "string"


def test_missing_value_rate_uses_partition_rows_and_counts_blank_values(
    specification, decision_expectation
):
    actual = specification["checks"]["missing_value_rate"]
    expected = decision_expectation["corrected_rule_semantics"][
        "missing_value_rate"
    ]

    assert actual["denominator_basis"] == expected["denominator_basis"]
    assert actual["denominator_basis"] == "all_records_in_partition"
    assert actual["missing_value_semantics"] == expected[
        "missing_value_semantics"
    ]
    assert actual["missing_value_semantics"] == [
        "null",
        "empty_string",
        "whitespace_only",
    ]


def test_duplicate_rule_uses_exact_composite_grain_and_staged_conflict_type(
    specification, decision_expectation
):
    actual = specification["checks"]["composite_key_duplicates"]
    expected = decision_expectation["corrected_rule_semantics"][
        "composite_key_duplicates"
    ]

    assert actual["key_columns"] == expected["key_columns"]
    assert actual["key_columns"] == ["partner_id", "payment_id"]
    assert actual["conflict_type"] == expected["conflict_type"]
    assert actual["conflict_type"] == "staged_key_conflict"


def test_amount_rule_treats_both_exact_limits_as_in_range(
    specification, decision_expectation
):
    actual = specification["checks"]["amount_range"]
    expected = decision_expectation["corrected_rule_semantics"]["amount_range"]

    assert actual["minimum_amount"] == expected["minimum_amount"]
    assert actual["maximum_amount"] == expected["maximum_amount"]
    assert actual["minimum_amount"] == 0.01
    assert actual["maximum_amount"] == 10000.0
    assert actual["minimum_inclusive"] is True
    assert actual["maximum_inclusive"] is True
    assert actual["boundary_classification"] == {
        "0.01": "in_range",
        "10000.00": "in_range",
    }


def test_reconciled_representative_outcomes_match_the_fixture(
    specification, decision_expectation
):
    actual = specification["reconciled_expected_outcomes"]
    expected = decision_expectation["reconciled_expected_outcomes"]

    assert actual == expected
    assert set(actual) == {
        "pay-clean-001",
        "pay-minimum-001",
        "pay-maximum-001",
        "pay-blank-001",
        "pay-conflict-a",
        "pay-conflict-b",
        "pay-over-maximum-001",
    }
    assert actual["pay-maximum-001"] == {
        "missing_value_rate": "pass",
        "composite_key_duplicates": "pass",
        "amount_range": "pass",
    }
    assert actual["pay-conflict-a"]["composite_key_duplicates"] == "fail"
    assert actual["pay-conflict-b"]["composite_key_duplicates"] == "fail"
    assert actual["pay-blank-001"]["missing_value_rate"] == "fail"
    assert actual["pay-over-maximum-001"]["amount_range"] == "fail"