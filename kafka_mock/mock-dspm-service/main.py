import os
import logging
import time
from kafka_handler import KafkaHandler
from policy_engine import PolicyEngine
from models import AssetDiscoveryEvent
from pydantic import ValidationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockDSPMService:
    """
    Mock DSPM Service that processes asset discovery events and 
    produces policy violations and remediation requests.
    """
    
    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.input_topic = os.getenv('INPUT_TOPIC', 'dspm.discovery.asset')
        self.violation_topic = os.getenv('VIOLATION_TOPIC', 'dspm.policy.violation')
        self.remediation_topic = os.getenv('REMEDIATION_TOPIC', 'dspm.remediation.requested')
        
        self.kafka_handler = KafkaHandler(self.kafka_bootstrap_servers)
        self.policy_engine = PolicyEngine()
        
        logger.info(f"Mock DSPM Service initialized")
        logger.info(f"Kafka Bootstrap Servers: {self.kafka_bootstrap_servers}")
        logger.info(f"Input Topic: {self.input_topic}")
        logger.info(f"Violation Topic: {self.violation_topic}")
        logger.info(f"Remediation Topic: {self.remediation_topic}")
    
    def process_asset_discovery(self, message: dict):
        """
        Process an asset discovery event and produce violation/remediation events.
        
        Args:
            message: Asset discovery event message
        """
        try:
            asset = AssetDiscoveryEvent(**message)
            logger.info(f"Processing asset: {asset.asset_id}")
            
            violations, remediations = self.policy_engine.evaluate_asset(asset)
            
            for violation in violations:
                violation_dict = violation.model_dump()
                self.kafka_handler.send_message(self.violation_topic, violation_dict)
                logger.info(
                    f"Published violation: {violation.violation_type.value} "
                    f"(severity: {violation.severity.value}) for asset {asset.asset_id}"
                )
            
            for remediation in remediations:
                remediation_dict = remediation.model_dump()
                self.kafka_handler.send_message(self.remediation_topic, remediation_dict)
                logger.info(
                    f"Published remediation: {remediation.remediation_type.value} "
                    f"(priority: {remediation.priority.value}) for asset {asset.asset_id}"
                )
            
            if not violations:
                logger.info(f"Asset {asset.asset_id} is compliant - no violations found")
        
        except ValidationError as e:
            logger.error(f"Invalid asset discovery event: {e}")
        except Exception as e:
            logger.error(f"Error processing asset discovery: {e}", exc_info=True)
    
    def start(self):
        """Start the mock DSPM service."""
        logger.info("Waiting for Kafka to be ready...")
        time.sleep(5)
        
        self.kafka_handler.create_producer()
        
        self.kafka_handler.create_consumer(
            topic=self.input_topic,
            group_id='mock-dspm-service'
        )
        
        logger.info("Mock DSPM Service started successfully")
        logger.info(f"Listening for asset discovery events on topic: {self.input_topic}")
        
        self.kafka_handler.consume_messages(self.process_asset_discovery)


if __name__ == "__main__":
    service = MockDSPMService()
    service.start()
