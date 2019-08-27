import json
from rs_utils import logger

class JsonStore:

    _data = {}

    def __init__(self):
        self._load()

    def _dump(self):
        logger.debug("", line=True)
        data_str = json.dumps(self._data, indent=4, sort_keys=True)
        logger.debug(data_str)

    def _load(self):
        with open(self._config_location, "r") as file:
            self._data = json.load(file)

    def _save(self):
        with open(self._config_location, "w") as file:
            file.write(
                json.dumps(
                    self._data,
                    indent=4,
                    sort_keys=True,
                )
            )
