import json
import logging

from kafka import KafkaProducer

logger = logging.getLogger(__name__)
logging.getLogger('kafka').setLevel(logging.WARNING)

class KafkaEventProducer:
    """
    Kafka producer for sending events to a specified topic.
    """

    def __init__(self, bootstrap_servers):
        """
        :param bootstrap_servers: Bootstrap servers for Kafka connection
        """
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send(self, topic, event):
        """
        Send an event to the specified Kafka topic.
        :param topic: Specified Kafka topic
        :param event: The event data to send
        """
        try:
            logger.debug(f"Publishing event to {topic}: {event}")
            self.producer.send(topic, event)
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
