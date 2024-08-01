import json
from app.common.code_logger import APP_LOGGER

def save_data_to_json(data, json_file):
    try:
        with open(json_file, "w") as outfile:
            json.dump(data, outfile)
    except Exception as e:
        APP_LOGGER.error("Error saving json ->", e)
        return False

    return True

def load_data_from_json(json_file):
    try:
        f = open(json_file)
        data_json = json.load(f)
        return data_json
    except Exception:
        return {}
