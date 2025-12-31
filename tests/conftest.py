from types import SimpleNamespace
from pathlib import Path
import pytest
from config.kafka_config import KAFKA_BOOTSTRAP_SERVERS
from utils.general import load_json
from utils.kafka_event_utils import build_asset_id, build_event_id
from utils.kafka_producer import KafkaEventProducer

@pytest.fixture(scope="session")
def producer() -> KafkaEventProducer:
    """
    Kafka producer fixture for sending events to Kafka.
    :return: KafkaEventProducer instance
    """
    return KafkaEventProducer(KAFKA_BOOTSTRAP_SERVERS)


@pytest.fixture
def get_test_parameters(request) -> SimpleNamespace:
    """
    Fixture to load test parameters from a JSON file based on the test type and asset type.
    :param request: Pytest request object
    :return: SimpleNamespace with test parameters
    """
    # helper to find the data directory relative to this file
    base_dir = Path(__file__).parent
    asset_data = load_json(base_dir / "data" / "assets.json")
    test_params = request.node.callspec.params
    test_type = test_params['test_type']
    asset_type = test_params['asset_type']
    specific_asset = asset_data.get(test_type, {}).get(asset_type, {})
    if specific_asset and "event_id" in specific_asset and not specific_asset["event_id"].startswith("evt_"):
        specific_asset["event_id"] = build_event_id(test_params['test_type'], test_params['asset_type'])
    if specific_asset and "asset_id" in specific_asset and '/' not in specific_asset["asset_id"]:
        specific_asset["asset_id"] = build_asset_id(specific_asset["asset_id"])
    return SimpleNamespace(**specific_asset)
