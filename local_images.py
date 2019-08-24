import json
from os import path

from rs_utils import logger
import config
from json_store import JsonStore
from remote_images import RemoteImages

class LocalImages(JsonStore):

    _config_location = path.join(
        config.DCD_DIR(),
        "config",
        "LOCAL_IMAGES.json",
    )

    def __init__(self):
        super(self.__class__, self).__init__()

    def BUILD(self, REGISTRY=None, TAG=None):
        logger.debug("Building image '%s:%s'" % (REGISTRY, TAG))
        logger.warning("docker build -t %s:%s ." % (REGISTRY, TAG))
        image_guid = REGISTRY + ":" + TAG
        error = False
        self._data[image_guid] = error
        self._save()

    def PUSH(self, REGISTRY=None, TAG=None):
        logger.debug("Pushing image '%s:%s'" % (REGISTRY, TAG))
        logger.warning("docker push %s:%s" % (REGISTRY, TAG))
        image_guid = REGISTRY + ":" + TAG
        remote_images = RemoteImages()
        remote_images.PUSH(IMAGE_GUID=image_guid)
