import logging
import time
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Tuple

from config.kafka_config import ASSET_TYPE, PROVIDER, ASSET_ID_PREFIX, TESTING_ENVIRONMENT, KAFKA_BOOTSTRAP_SERVERS, \
    DISCOVERY_TOPIC, VIOLATION_TOPIC, REMEDIATION_TOPIC
from utils.kafka_consumer import KafkaEventConsumer


def build_asset_id(asset_id) -> str:
    """
    Builds a full asset ID for testing environment.
    :param asset_id: Asset identifier
    :return: Full asset ID string
    """
    return f"{ASSET_ID_PREFIX}{TESTING_ENVIRONMENT}/{asset_id}"

def build_asset_event(
    event_id,
    asset_id,
    encryption_enabled,
    public_access,
    data_classification,
    tags,
    timestamp_hours_diff=0,
) -> dict:
    """
    Builds an asset discovery event.
    :param event_id: Event identifier
    :param asset_id: Asset identifier
    :param encryption_enabled: Encryption status
    :param public_access: Public access status
    :param data_classification: Classification level
    :param tags: Tags dictionary
    :param timestamp_hours_diff: Time difference in hours for the timestamp
    :return: Asset discovery event dictionary
    """
    timestamp = (datetime.utcnow() - timedelta(hours=timestamp_hours_diff)).isoformat(timespec="seconds") + "Z"
    return {
        "event_id": event_id,
        "timestamp": timestamp,
        "asset_id": asset_id,
        "asset_type": ASSET_TYPE,
        "cloud_provider": PROVIDER,
        "region": "us-east-1",
        "discovered_by": "pytest",
        "metadata": {
            "encryption_enabled": encryption_enabled,
            "public_access": public_access,
            "data_classification": data_classification,
            "tags": tags
        }
    }


def build_event_id(*args) -> str:
    """
    Builds a unique event ID based on provided arguments.
    :param args: Arguments to include in the event ID
    :return: Unique event ID string
    """
    return f"evt_{'_'.join(str(arg) for arg in args)}_{uuid.uuid4()}"


def send_event(producer, *args, **kwargs):
    """
    Sends an asset discovery event to the Kafka topic.
    :param producer: KafkaEventProducer instance
    :param args: Positional arguments for event parameters:
            0 - event_id,
            1 - asset_id,
            2 - is_encrypted,
            3 - is_public,
            4 - classification,
            5 - tags,
            6 - timestamp_hours_diff,
            7 - repeat
    :param kwargs: Keyword arguments for event parameters
    """
    params = kwargs.get("params", {})
    params_elements = ["event_id", "asset_id", "is_encrypted", "is_public", "classification", "tags", "timestamp_hours_diff", "repeat"]
    for indx, param in enumerate(args):
        if isinstance(params, dict):
            params[params_elements[indx]] = param
        else:
            setattr(params, params_elements[indx], param)

    if kwargs:
        if isinstance(params, dict):
            params = params | kwargs
        else:
            for key, value in kwargs.items():
                if key != "params":
                    setattr(params, key, value)

    if isinstance(params, dict):
        params = SimpleNamespace(**params)

    event_id = params.event_id
    asset_id = params.asset_id
    is_encrypted = getattr(params, "is_encrypted", False)
    is_public = getattr(params, "is_public", False)
    classification = getattr(params, "classification", "PCI")
    timestamp_hours_diff = getattr(params, "timestamp_hours_diff", 0)
    tags = getattr(params, "tags", {})
    repeat = getattr(params, "repeat", 1)

    logging.info(f"Sending event {event_id} with asset_id {asset_id}")
    asset = build_asset_event(event_id, asset_id, encryption_enabled=is_encrypted, public_access=is_public,
                              data_classification=classification, tags=tags, timestamp_hours_diff=timestamp_hours_diff)
    for _ in range(repeat):
        producer.send(DISCOVERY_TOPIC, asset)


def consume_with_wait(topic, asset_id, timeout=1) -> list:
    """
    Consumes events from a Kafka topic, waiting up to a specified timeout for events with the given asset_id.
    :param topic: Kafka topic to consume from
    :param asset_id: Asset identifier to filter events
    :param timeout: Maximum wait time in seconds
    :return: List of events matching the asset_id
    """
    start = time.time()
    results = []

    logging.info(f"Waiting for event {asset_id} with topic {topic}")
    while time.time() - start < timeout:
        events = KafkaEventConsumer(topic, KAFKA_BOOTSTRAP_SERVERS).consume()
        results = [e for e in events if e["asset_id"] == asset_id]
        if results:
            logging.info(f"Found {len(results)} events")
            return results
        time.sleep(1)

    logging.info(f"No events found for asset_id {asset_id} with topic {topic} within timeout")
    return results


def get_violation_remediation(asset_id, get_violation=True, get_remediation=True, get_last_only=False,
                              specific_event_id=None) -> Tuple[list | dict | None, list | dict | None]:
    """
    Retrieves violation and remediation events for a given asset_id.
    :param asset_id: Asset identifier
    :param get_violation: Determine whether to get violation events
    :param get_remediation: Determine whether to get remediation events
    :param get_last_only: Whether to return only the last event
    :param specific_event_id: Specific source event ID to filter violations
    :return: Tuple of violation and remediation events
    """
    violation = consume_with_wait(VIOLATION_TOPIC, asset_id) if get_violation else []
    remediation = consume_with_wait(REMEDIATION_TOPIC, asset_id) if get_remediation else []
    if get_last_only:
        violation = violation[-1] if violation else None
        remediation = remediation[-1] if remediation else None
    if specific_event_id:
        violation = [v for v in violation if v["source_event_id"] == specific_event_id] if violation else []
        violation_ids = {v["event_id"] for v in violation} if violation else []
        remediation = [r for r in remediation if r["violation_event_id"] in violation_ids] if remediation else []
    return violation, remediation
