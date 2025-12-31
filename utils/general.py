import json
import logging

logger = logging.getLogger(__name__)

def load_json(path):
    """
    Load a JSON file from the specified path.
    :param path: Path to the JSON file
    :return: Parsed JSON data or empty dict on failure
    """
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading JSON from {path}: {e}")
        return {}
