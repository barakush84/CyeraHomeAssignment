from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class KafkaHandler:
    """Handles Kafka consumer and producer operations."""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.producer = None
    
    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        """Create a Kafka consumer."""
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=self._deserialize_json,
            )
            logger.info(f"Consumer created for topic: {topic}")
            return self.consumer
        except KafkaError as e:
            logger.error(f"Failed to create consumer: {e}")
            raise
    
    def _deserialize_json(self, message_bytes):
        """Safely deserialize JSON messages with error handling."""
        try:
            return json.loads(message_bytes.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize message as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error deserializing message: {e}")
            return None
    
    def create_producer(self) -> KafkaProducer:
        """Create a Kafka producer."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
            )
            logger.info("Producer created")
            return self.producer
        except KafkaError as e:
            logger.error(f"Failed to create producer: {e}")
            raise
    
    def send_message(self, topic: str, message: dict):
        """Send a message to a Kafka topic."""
        try:
            future = self.producer.send(topic, value=message)
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Message sent to {topic} - "
                f"partition: {record_metadata.partition}, "
                f"offset: {record_metadata.offset}"
            )
        except KafkaError as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            raise
    
    def consume_messages(self, callback: Callable[[dict], None]):
        """
        Consume messages and process them with the callback function.
        
        Args:
            callback: Function to process each message
        """
        try:
            logger.info("Starting to consume messages...")
            for message in self.consumer:
                try:
                    # Skip messages that failed deserialization
                    if message.value is None:
                        logger.warning("Skipping message with invalid JSON format")
                        continue
                    
                    logger.info(f"Received message: {message.value}")
                    callback(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
        finally:
            self.close()
    
    def close(self):
        """Close consumer and producer connections."""
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer closed")
        if self.producer:
            self.producer.close()
            logger.info("Producer closed")
