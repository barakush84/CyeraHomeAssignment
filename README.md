# CyeraHomeAssignment

Short description
-----------------
Small Python test-suite and utilities that validate Kafka-related events and asset data. Tests use `pytest` and produce an auto-generated HTML report.

Project structure
-----------------
```text
CyeraHomeAssignment/
├── config/
│   └── kafka_config.py       # Configuration modules
├── tests/
│   ├── data/                 # Test data files (e.g. assets.json)
│   ├── conftest.py           # Pytest fixtures
│   └── test_kafka.py         # Test scenarios
├── utils/                    # Helper modules and Kafka utilities
│   ├── assertions.py
│   ├── general.py
│   ├── kafka_consumer.py
│   ├── kafka_event_utils.py
│   └── kafka_producer.py
├── .gitignore
├── pytest.ini                # Pytest configuration
├── README.md
├── requirements.txt          # Python dependencies
└── TEST_PLAN.md              # Test planning document
```

Requirements
------------
- Python 3.11 recommended.
- Git and a command-line terminal.
- Docker Desktop (for running the Kafka mock server).
- Kafka server running on `localhost:9092`.



Kafka Mock Server
-------------------
This project requires a local Kafka environment. A pre-configured mock server is provided in the `kafka_mock` directory.

To start the mock server:
1. Open a terminal.
2. Navigate to the mock server directory and start the services:
   ```bash
   cd kafka_mock
   docker-compose up -d
   ```
   
For more details, see the [Kafka Mock Server README](kafka_mock/README.md).

Run tests
-------------------
1. Open your terminal (PowerShell, Command Prompt, or Bash).
2. Clone or open the project and change directory:
   - `cd /path/to/CyeraHomeAssignment`
3. Create and activate a virtual environment:
   
   **Windows:**
   - `python -m venv .venv`
   - `.venv\Scripts\activate`

   **Linux / macOS:**
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`

4. Install requirements:
   - `pip install -r requirements.txt`
5. Run the full test suite (pytest is configured by `pytest.ini`):
   - `pytest`
   - or `python -m pytest`

Notes about pytest configuration
-------------------------------
- `pytest.ini` enables CLI logging and sets `addopts` to rerun failing tests up to 3 times, keep a 1s delay between reruns, and generate a self-contained HTML report at:
  - `reports/test_report.html`
- The HTML report is created automatically after the test run. To open it:
  - **Windows**: `start reports\test_report.html`
  - **Linux**: `xdg-open reports/test_report.html`
  - **macOS**: `open reports/test_report.html`
- You can run a single test file:
  - `pytest tests\test_kafka.py`
- To run a single test by node id:
  - `pytest tests\test_kafka.py::test_name`

