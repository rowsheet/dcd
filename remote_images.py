import json
from os import path

from rs_utils import logger
import config
from json_store import JsonStore

class RemoteImages(JsonStore):

    _config_location = path.join(
        config.DCD_DIR(),
        "config",
        "REMOTE_IMAGES.json",
    )

    def __init__(self):
        super(self.__class__, self).__init__()

    def PUSH(self, IMAGE_GUID=None):
        logger.success("Remove recieving image '%s'..." % IMAGE_GUID)
        error = False
        self._data[IMAGE_GUID] = error
        self._save()
