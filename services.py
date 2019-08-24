import json
from os import path

from rs_utils import logger
import config
from json_store import JsonStore

class Services(JsonStore):

    _config_location = path.join(
        config.DCD_DIR(),
        "config",
        "SERVICES.json",
    )

    def __init__(self):
        super(self.__class__, self).__init__()

    def CREATE(self,
            IMAGE_NAME=None,
            HOST_NAME=None,
            SERVICE_NAME=None,
            ENV_VARS=None,
            COMMON_SERVICE_NAME=None,
            CLIENT_NAME=None, 
        ):
        logger.debug("Creating service '%s' for client '%s'" % (
            COMMON_SERVICE_NAME,CLIENT_NAME))
        logger.warning("\tIMAGE_NAME: %s" % IMAGE_NAME)
        logger.warning("\tHOST_NAME: %s" % HOST_NAME)
        logger.warning("\tSERVICE_NAME: %s" % SERVICE_NAME)
        logger.warning("\tENV_VARS: %s" % ENV_VARS)
        logger.warning("\tCOMMON_SERVICE_NAME: %s" % COMMON_SERVICE_NAME)
        logger.warning("\tCLIENT_NAME: %s" % CLIENT_NAME)

        info_dict = {
            "IMAGE_NAME": IMAGE_NAME,
            "HOST_NAME": HOST_NAME,
            "SERVICE_NAME": SERVICE_NAME,
            "ENV_VARS": ENV_VARS,
            "COMMON_SERVICE_NAME": COMMON_SERVICE_NAME,
            "CLIENT_NAME": CLIENT_NAME,
        }
        self._data[SERVICE_NAME] = info_dict
        self._save()

    def PUSH(self, REGISTRY=None, TAG=None):

        image_guid = REGISTRY + ":" + TAG
