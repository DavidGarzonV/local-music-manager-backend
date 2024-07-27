import json

from app.common.code_logger import APP_LOGGER


def save_data_to_json(data, json_file):
    with open(json_file, "w") as outfile:
        json.dump(data, outfile)


def load_data_from_json(json_file):
    try:
        f = open(json_file)
        data_json = json.load(f)
        return data_json
    except Exception:
        APP_LOGGER.error("Error loading data from json file")
        return {}
