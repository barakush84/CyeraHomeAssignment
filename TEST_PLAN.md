# Kafka Module \- High Level Test Plan


## 1. Overview
This document describes a high\-level test plan for the Kafka event processing module exercised by `tests/test_kafka.py`. The tests validate that source discovery events produce expected violation and remediation events, with correct fields, ordering, correlation and performance characteristics.

## 2. Scope
1. Functional validation of violation and remediation event generation.
2. Event correlation and metadata correctness.
3. Ordering, duplication and isolation behavior across assets.
4. Timing and performance thresholds for event emission.
5. Resilience to large payloads (large tag values).
6. Exclusions: deep unit tests of producer internals, downstream consumer service internals, time\-based due date logic (not reliable).

## 3. Objectives
1. Verify correct event types and payload fields are emitted.
2. Confirm remediation logic and expected priorities/types.
3. Ensure events are correlated to source event IDs.
4. Validate ordering and concurrency behavior.
5. Check system tolerance for large attribute sizes.

## 4. Test Items (mapped to test functions)
1. `test_compliant_asset_generates_no_events`  
   - Type: Functional / Negative  
   - Purpose: Ensure compliant asset yields no violation or remediation events.  
   - Success: No events found for the asset.

2. `test_unencrypted_triggers_violation_and_remediation`  
   - Type: Functional / Parameterized  
   - Purpose: Unencrypted classified data triggers specific violation and remediation.  
   - Success: Violation and remediation match expected types, severities and priorities.

3. `test_missing_owner_tag_has_no_remediation`  
   - Type: Functional  
   - Purpose: Missing owner tag produces low severity violation and no remediation.  
   - Success: Violation type is MISSING_OWNER_TAG, remediation absent.

4. `test_public_access_triggers_high_severity_violation`  
   - Type: Functional  
   - Purpose: Public access enabled produces high severity violation and remediation.  
   - Success: PUBLIC_ACCESS_ENABLED violation and DISABLE_PUBLIC_ACCESS remediation present.

5. `test_event_correlation_chain`  
   - Type: Integration / Correlation  
   - Purpose: Remediation references violation event ID and violation references source event ID.  
   - Success: `violation.source_event_id == source_event_id` and `remediation.violation_event_id == violation.event_id`.

6. `test_violation_emitted_within_3_seconds`  
   - Type: Performance / Timing  
   - Purpose: Violation emitted within acceptable time window.  
   - Success: Time delta < 3 seconds.

7. `test_duplicate_event_id_produces_multiple_violations`  
   - Type: Functional / Idempotency behavior  
   - Purpose: Duplicate source event IDs produce multiple violations (system treats repeats as separate).  
   - Success: N violations and N remediations produced when repeated N times.

8. `test_each_duplicate_has_valid_event_chain`  
   - Type: Functional / Correlation  
   - Purpose: Each duplicate has matching remediation pointing to its violation.  
   - Success: For each pair, remediation.violation_event_id == violation.event_id.

9. `test_violation_has_required_fields`  
   - Type: Schema / Contract  
   - Purpose: Violation event contains required fields (IDs, policy, description, timestamps).  
   - Success: Required field set is subset of violation keys.

10. `test_remediation_has_required_fields`  
    - Type: Schema / Contract  
    - Purpose: Remediation event contains required fields (assigned_to, due_date, auto_remediate, etc.).  
    - Success: Required field set is subset of remediation keys.

11. `test_large_tag_values_do_not_break_processing`  
    - Type: Robustness / Payload size  
    - Purpose: Very large tag values are handled without failure.  
    - Success: Violation referencing the large payload event is produced.

12. `test_events_for_multiple_assets_are_isolated`  
    - Type: Functional / Isolation  
    - Purpose: Events for different assets do not cross\-contaminate.  
    - Success: Violations returned per asset belong only to that asset.

13. `test_concurrent_distinct_events_produce_matching_violations`  
    - Type: Concurrency / Integration  
    - Purpose: Multiple concurrent source events produce matching violations.  
    - Success: All source event IDs appear in produced violations.

14. `test_event_order_preserved_for_quick_sends`  
    - Type: Ordering / Sequence  
    - Purpose: Quick sequential sends preserve order in emitted events (last N checked).  
    - Success: Observed event order equals send order for the last N events.

## 5. Test Types and Techniques
1. Integration tests using test Kafka cluster (local or ephemeral container).  
2. Consumer assertions: read from violation and remediation topics with timeouts.  
3. Parameterized tests for classification variations.  
4. Load/concurrency tests for bursts and duplicate sends.  
5. Schema validation for event payloads.  
6. Timebox-based performance assertions (keep conservative thresholds).

## 6. Test Data
1. Deterministic event IDs generated via `build_event_id` fixture function.  
2. Asset IDs via `build_asset_id`.  
3. Tags including owner and large\-value scenarios.  
4. Parameterized fixtures for classification, severities, remediation expectations.

## 7. Test Environment & Prerequisites
1. Running Kafka instance accessible to tests (local Docker Compose or test cluster).  
2. Topics for discovery, violations and remediations configured and cleanable between tests.  
3. Fixtures available: `producer`, `get_test_parameters`, utilities to send/read events.  
4. Test runner: `pytest`.  
5. Proper configuration for timeouts and consumer group isolation.

## 8. Execution Strategy
1. Run tests in an isolated environment with Kafka topics reset between test sessions.  
2. Run schema/contract tests first, then functional, then performance/concurrency.  
3. For flaky timing tests, increase consumer timeout or convert to retries with backoff rather than strict sleeps.

## 9. Entry / Exit Criteria
1. Entry: Development complete, fixtures implemented, Kafka environment reachable.  
2. Exit: All functional and schema tests pass; timing tests within agreed thresholds; no critical regressions.

## 10. Risks and Mitigations
1. Timing flakiness: mitigate by increasing timeouts and using retry loops.  
2. Test pollution via persistent topics: isolate consumer groups and purge topics between tests.  
3. Large payload memory pressure: cap large test sizes in CI; run stress cases separately.

## 11. Reporting and Logging
1. Capture produced and consumed event payloads for failed tests.  
2. Include timestamps and consumer offsets in logs to aid debugging.  
3. Aggregate test failures by category (schema, correlation, performance).

## 12. Maintenance Notes
1. Keep parameter fixtures in sync with policy changes (violation types, remediation types/priorities).  
2. If due date logic becomes reliable, reintroduce the parameterized due date tests in a separate suite.
