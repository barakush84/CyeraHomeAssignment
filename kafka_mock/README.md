## Running the Mock Service

### Prerequisites

Before starting, ensure you have Docker and Docker Compose installed:

- **Docker Desktop** (includes Docker Compose): [Install Docker](https://docs.docker.com/get-docker/)
- Verify installation:
  ```bash
  docker --version
  docker-compose --version
  ```

**Note:** All Python dependencies for the mock service are automatically installed inside the Docker container. You do not need to manually install `requirements.txt`.

### Starting the Infrastructure

```bash
cd home-assignment
docker-compose up -d
```

Allow approximately 30 seconds for all services to initialize.

### Verifying Service Status

```bash
docker-compose logs -f mock-dspm-service
# Expected output: "Mock DSPM Service started successfully"
```

### Kafka Configuration

- **Bootstrap Server:** `localhost:9092`
- **Topics:** Automatically created upon service startup

### Viewing Logs

```bash
# View service logs
docker-compose logs -f mock-dspm-service

# List available topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Consume messages from a topic (press Ctrl+C to stop)
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dspm.policy.violation \
  --from-beginning

# Optional: Limit to first N messages
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dspm.policy.violation \
  --from-beginning \
  --max-messages 5
```

### Stopping the Infrastructure

```bash
docker-compose down
```

---

**We look forward to reviewing your submission. Good luck!**
