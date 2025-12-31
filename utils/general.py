import json

def load_json(path):
    """
    Load a JSON file from the specified path.
    :param path: Path to the JSON file
    :return: Parsed JSON data
    """
    with open(path) as f:
        return json.load(f)
