import json
from kafka import KafkaConsumer

class KafkaEventConsumer:
    """
    Kafka consumer for consuming events from a specified topic.
    """
    def __init__(self, topic, bootstrap_servers, timeout=1):
        """
        :param topic: Specified Kafka topic to consume from
        :param bootstrap_servers: Bootstrap servers for Kafka connection
        :param timeout: Maximum time to wait for messages (in seconds)
        """
        self.topic = topic
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=timeout * 1000,
            enable_auto_commit=False  # Explicitly disable to stop warning
        )

    def consume(self):
        """
        Consume messages from the specified Kafka topic.
        :return: List of consumed messages
        """
        return [msg.value for msg in self.consumer]
