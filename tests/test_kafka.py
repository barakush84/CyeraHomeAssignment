import time
import pytest
from config.kafka_config import DiscoveryDataClassification, ViolationType, ViolationSeverity, \
    RemediationType, RemediationPriority
from utils.assertions import assert_violation_remediation
from utils.kafka_event_utils import build_asset_id, send_event, get_violation_remediation, build_event_id


class TestKafka:
    def test_compliant_asset_generates_no_events(self, producer):
        """
        Test that a compliant asset does not generate any violation or remediation events.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("test_ok")
        asset_id = build_asset_id("reports")
        tags = {"owner": "team"}
        send_event(producer, event_id, asset_id, True, False, DiscoveryDataClassification.INTERNAL, tags)
        violation, remediation = get_violation_remediation(asset_id)
        assert not any(v["asset_id"] == asset_id for v in violation)
        assert not any(r["asset_id"] == asset_id for r in remediation)

    @pytest.mark.parametrize("test_type, asset_type", [pytest.param("unencrypted", "pii", id="unencrypted_pii"),
                                                       pytest.param("unencrypted", "pii", id="unencrypted_pci")])
    def test_unencrypted_triggers_violation_and_remediation(self, producer, get_test_parameters, test_type, asset_type):
        """
        Test that unencrypted data with specific classifications triggers the appropriate violation and remediation.
        :param producer: Kafka producer (from fixture)
        :param get_test_parameters: Fixture to get test parameters
        :param test_type: Type of test (e.g., "unencrypted")
        :param asset_type: Type of asset (e.g., "pii" or "pci")
        """
        params = get_test_parameters
        send_event(producer, params=params)
        violation, remediation = get_violation_remediation(params.asset_id)
        assert_violation_remediation(violation, params.violation_type, params.violation_severity,
                                     params.event_id, remediation, params.remediation_type, params.remediation_priority,
                                     params.asset_id)

    def test_missing_owner_tag_has_no_remediation(self, producer):
        """
        Test that a missing owner tag triggers a low severity violation without remediation.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("no_owner")
        asset_id = build_asset_id("no-owner")
        send_event(producer, event_id, asset_id, True, False, DiscoveryDataClassification.INTERNAL)
        violation, remediation = get_violation_remediation(asset_id)
        assert_violation_remediation(violation, ViolationType.MISSING_OWNER_TAG, ViolationSeverity.LOW, event_id,
                                     remediation, asset_id=asset_id, remediation_expected=False)

    def test_public_access_triggers_high_severity_violation(self, producer):
        """
        Test that public access enabled triggers a high severity violation and remediation.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("public")
        asset_id = build_asset_id("public")
        tags = {"owner": "ops"}
        send_event(producer, event_id, asset_id, True, True, DiscoveryDataClassification.INTERNAL, tags)
        violation, remediation = get_violation_remediation(asset_id)
        assert_violation_remediation(violation, ViolationType.PUBLIC_ACCESS_ENABLED, ViolationSeverity.HIGH, event_id,
                                     remediation, RemediationType.DISABLE_PUBLIC_ACCESS, RemediationPriority.HIGH, asset_id)

    def test_event_correlation_chain(self, producer):
        """
        Test that the violation and remediation events correctly reference the source event ID.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("chain")
        asset_id = build_asset_id("chain")
        tags = {"owner": "sec"}
        send_event(producer, event_id, asset_id, False, False, DiscoveryDataClassification.PII, tags)
        violation, remediation = get_violation_remediation(asset_id, get_last_only=True)
        assert violation["source_event_id"] == event_id
        assert remediation["violation_event_id"] == violation["event_id"]

    def test_violation_emitted_within_3_seconds(self, producer):
        """
        Test that a violation event is emitted within 3 seconds of sending the source event.
        Timeout for consuming is set to 1 second, so this test assumes processing time is under 2 seconds.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("timing")
        asset_id = build_asset_id("timing")
        tags = {"owner": "qa"}
        start = time.time()
        send_event(producer, event_id, asset_id, True, True, DiscoveryDataClassification.PII, tags)
        violation, _ = get_violation_remediation(asset_id, get_last_only=True)
        assert time.time() - start < 3

    def test_duplicate_event_id_produces_multiple_violations(self, producer):
        """
        Test that sending multiple events with the same event ID produces multiple violation and remediation events.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("dup")
        asset_id = build_asset_id("dup")
        tags = {"owner": "ops"}
        send_event(producer, event_id, asset_id, False, False, DiscoveryDataClassification.PII, tags, repeat=3)
        violation, remediation = get_violation_remediation(asset_id, specific_event_id=event_id)
        assert len(violation) == 3
        assert len(remediation) == 3

    def test_each_duplicate_has_valid_event_chain(self, producer):
        """
        Test that each duplicate event ID produces violation and remediation events that correctly reference the source event ID.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("dup-chain")
        asset_id = build_asset_id("dup-chain")
        tags = {"owner": "team"}
        send_event(producer, event_id, asset_id, False, False, DiscoveryDataClassification.PII, tags, repeat=3)
        violation, remediation = get_violation_remediation(asset_id, specific_event_id=event_id)
        assert len(violation) == 3
        assert len(remediation) == 3
        for v, r in zip(violation, remediation):
            assert r["violation_event_id"] == v["event_id"]

    def test_violation_has_required_fields(self, producer):
        """
        Test that the violation event contains all required fields.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("vio_fields")
        asset_id = build_asset_id("vio_fields")
        send_event(producer, event_id, asset_id, False, False, DiscoveryDataClassification.PII, {"owner": "eng"})
        violation, _ = get_violation_remediation(asset_id, get_last_only=True)
        required = {"event_id", "asset_id", "violation_type", "severity", "source_event_id", "timestamp",
                    "policy_id", "policy_name", "description"}
        assert required.issubset(set(violation.keys()))

    def test_remediation_has_required_fields(self, producer):
        """
        Test that the remediation event contains all required fields.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("rem_fields")
        asset_id = build_asset_id("rem_fields")
        send_event(producer, event_id, asset_id, True, True, DiscoveryDataClassification.PII, {"owner": "sec"})
        _, remediation = get_violation_remediation(asset_id, get_last_only=True)
        required = {"event_id", "asset_id", "violation_event_id", "remediation_type", "priority", "timestamp", "auto_remediate", "assigned_to", "due_date"}
        assert required.issubset(set(remediation.keys()))

    def test_large_tag_values_do_not_break_processing(self, producer):
        """
        Test that large tag values do not break event processing.
        :param producer: Kafka producer (from fixture)
        """
        event_id = build_event_id("large_tag")
        asset_id = build_asset_id("large_tag")
        large_value = "x" * 50_000
        tags = {"owner": large_value}
        send_event(producer, event_id, asset_id, False, False, DiscoveryDataClassification.PII, tags)
        violation, _ = get_violation_remediation(asset_id, specific_event_id=event_id)
        assert any(v["asset_id"] == asset_id and v.get("source_event_id") == event_id for v in violation)

    def test_events_for_multiple_assets_are_isolated(self, producer):
        """
        Test that events for multiple distinct assets produce isolated violation events.
        :param producer: Kafka producer (from fixture)
        """
        event_a = build_event_id("multi_a")
        asset_a = build_asset_id("multi_a")
        event_b = build_event_id("multi_b")
        asset_b = build_asset_id("multi_b")
        send_event(producer, event_a, asset_a, False, False, DiscoveryDataClassification.PII, {"owner": "team-a"})
        send_event(producer, event_b, asset_b, False, False, DiscoveryDataClassification.PII, {"owner": "team-b"})
        violation_a, _ = get_violation_remediation(asset_a)
        violation_b, _ = get_violation_remediation(asset_b)
        assert all(v["asset_id"] == asset_a for v in violation_a)
        assert all(v["asset_id"] == asset_b for v in violation_b)

    def test_concurrent_distinct_events_produce_matching_violations(self, producer):
        """
        Test that concurrently sent distinct events produce matching violation events.
        :param producer: Kafka producer (from fixture)
        """
        asset_id = build_asset_id("concurrent")
        event_ids = [build_event_id(f"concurrent_{i}") for i in range(5)]
        for eid in event_ids:
            send_event(producer, eid, asset_id, False, False, DiscoveryDataClassification.PII, {"owner": "ops"})
        violation, _ = get_violation_remediation(asset_id)
        observed_event_ids = {v.get("source_event_id") or v.get("event_id") for v in violation}
        assert set(event_ids).issubset(observed_event_ids)

    def test_event_order_preserved_for_quick_sends(self, producer):
        """
        Test that events sent in quick succession preserve their order in the violation events.
        :param producer: Kafka producer (from fixture)
        """
        asset_id = build_asset_id("order")
        event_ids = [build_event_id(f"order_{i}") for i in range(4)]
        for eid in event_ids:
            send_event(producer, eid, asset_id, False, False, DiscoveryDataClassification.PII, {"owner": "qa"})
            time.sleep(0.01)
        violation, _ = get_violation_remediation(asset_id)
        # To avoid issues with extra events from retries, only check the last N events
        observed = [v.get("source_event_id") or v.get("event_id") for v in violation][-len(event_ids):]
        assert observed == event_ids

    # ToDo: event timestamp is ignored and auto-set by the system, so due_date-based tests may not work as intended.
    # @pytest.mark.parametrize("test_type, asset_type, due_date_hours_diff, should_have_remediation", [
    #     pytest.param("due_date", "pii", 23, True, id="due_date_pii_within_threshold"),
    #     pytest.param("due_date", "pii", 25, False, id="due_date_pii_beyond_threshold"),
    #     pytest.param("due_date", "pci", 23, True, id="due_date_pci_within_threshold"),
    #     pytest.param("due_date", "pci", 25, False, id="due_date_pci_beyond_threshold"),
    #     pytest.param("due_date", "public_access", 71, True, id="due_date_public_within_threshold"),
    #     pytest.param("due_date", "public_access", 73, False, id="due_date_public_beyond_threshold")
    # ])
    # def test_due_date(self, producer, get_test_parameters, test_type, asset_type, due_date_hours_diff,
    #                   should_have_remediation):
    #     """
    #     Test that due date affects remediation generation based on defined thresholds.
    #     :param producer: Kafka producer (from fixture)
    #     :param get_test_parameters: Fixture to get test parameters
    #     :param test_type: Type of test from config file (e.g., "due_date")
    #     :param asset_type: Type of asset from config file (e.g., "pii", "pci", "public_access")
    #     :param due_date_hours_diff: Hours difference to set due date
    #     :param should_have_remediation: Whether remediation is expected to be generated
    #     """
    #     params = get_test_parameters
    #     send_event(producer, params=params, timestamp_hours_diff=due_date_hours_diff)
    #     violation, remediation = get_violation_remediation(params.asset_id)
    #     assert_violation_remediation(violation, params.violation_type, params.violation_severity,
    #                                  params.event_id, remediation, params.remediation_type, params.remediation_priority,
    #                                  params.asset_id, remediation_expected=should_have_remediation)
