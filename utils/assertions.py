def assert_violation_event(event, expected_type, expected_severity, source_event_id, asset_id=None) -> dict:
    """
    Asserts that a violation event matches the expected type and severity.
    :param event: List or dict representing the violation event
    :param expected_type: Expected violation type
    :param expected_severity: Expected violation severity
    :param source_event_id: Source event identifier
    :param asset_id: Optional asset identifier
    :return: The matched violation event as a dict
    """
    if isinstance(event, list):
        if not asset_id:
            raise ValueError("asset_id must be provided when event is a list")
        event = next(v for v in event if v["asset_id"] == asset_id and v["source_event_id"] == source_event_id)

    assert event["violation_type"] == expected_type
    assert event["severity"] == expected_severity
    return event

def assert_remediation_event(event, expected_type, priority, asset_id=None, violation_id=None):
    """
    Asserts that a remediation event matches the expected type and priority.
    :param event: List or dict representing the remediation event
    :param expected_type: Expected remediation type
    :param priority: Expected remediation priority
    :param asset_id: Optional asset identifier
    :param violation_id: Optional violation event identifier
    """
    all_remediation_events = event
    if isinstance(event, list):
        if not asset_id:
            raise ValueError("asset_id must be provided when event is a list")
        if violation_id:
            event = next(v for v in all_remediation_events if v["asset_id"] == asset_id and v["violation_event_id"] == violation_id)
        else:
            event = next(v for v in all_remediation_events if v["asset_id"] == asset_id)

    assert event["remediation_type"] == expected_type
    assert event["priority"] == priority

def assert_violation_remediation(*args, **kwargs):
    """
    Asserts violation and remediation events based on expected parameters.
    :param args: args for assertion parameters
    :param kwargs: kwargs for assertion parameters
    """
    params = get_assertion_params(*args, **kwargs)
    violation = None
    event_violation = args[0]
    violation_expected = params.get("violation_expected", True)
    remediation_expected = params.get("remediation_expected", True)
    if violation_expected:
        violation = assert_violation_event(
            event_violation,
            expected_type=params.get("expected_violation_type"),
            expected_severity=params.get("expected_violation_severity"),
            source_event_id=params.get("source_event_id"),
            asset_id=params.get("asset_id")
        )
    else:
        assert len(event_violation) == 0  # No violation expected

    if remediation_expected:
        assert_remediation_event(
            params.get("event_remediation"),
            expected_type=params.get("expected_remediation_type"),
            priority=params.get("expected_remediation_priority"),
            asset_id=params.get("asset_id"),
            violation_id=violation['event_id'] if violation else None
        )

    else:
        assert len(params.get("event_remediation")) == 0  # No remediation expected

def get_assertion_params(*args, **kwargs) -> dict:
    """
    Helper to build a params dictionary for assertion functions.
    :param args: args for parameters
    :param kwargs: kwargs for parameters
    :return: Dictionary of parameters
    """
    params_dict = kwargs.get("params", {})
    if not params_dict:
        params_elements = ["event_violation", "expected_violation_type", "expected_violation_severity",
                           "source_event_id","event_remediation", "expected_remediation_type",
                           "expected_remediation_priority", "asset_id", "violation_expected",
                           "remediation_expected", "due_date"]
        for indx, param in enumerate(args):
            params_dict[params_elements[indx]] = param
        params_dict = params_dict | kwargs
    return params_dict