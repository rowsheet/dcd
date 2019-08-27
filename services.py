import json
from os import path
import docker

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

    def DELETE(self, SERVICE_NAME=None):
        client = docker.from_env()
        services = client.services.list()
        names_to_ids = {service.name: service.id for service in services}
        if SERVICE_NAME in names_to_ids:
            id = names_to_ids[SERVICE_NAME]
            service = client.services.get(id)
            service.remove()

    def MARK_TEST_PASSED(self, SERVICE_NAME=None):
        self._data[SERVICE_NAME]["TEST_STATUS"] = "TEST_PASSED"
        self._save()

    def UPGRADE(self,
            IMAGE_NAME=None,
            HOST_NAME=None,
            SERVICE_NAME=None,
            ENV_VARS={},
            COMMON_SERVICE_NAME=None,
            CLIENT_NAME=None, 
            TEST_STATUS="WAITING_APPROVAL",
        ):
        logger.debug("Upgrading service '%s' for client '%s'" % (
            COMMON_SERVICE_NAME,CLIENT_NAME))
        logger.warning("\tIMAGE_NAME: %s" % IMAGE_NAME)
        logger.warning("\tHOST_NAME: %s" % HOST_NAME)
        logger.warning("\tSERVICE_NAME: %s" % SERVICE_NAME)
        logger.warning("\tENV_VARS: %s" % ENV_VARS)
        logger.warning("\tCOMMON_SERVICE_NAME: %s" % COMMON_SERVICE_NAME)
        logger.warning("\tCLIENT_NAME: %s" % CLIENT_NAME)
        logger.warning("\tTEST_STATUS: %s" % TEST_STATUS)

        info_dict = {
            "IMAGE_NAME": IMAGE_NAME,
            "HOST_NAME": HOST_NAME,
            "SERVICE_NAME": SERVICE_NAME,
            "ENV_VARS": ENV_VARS,
            "COMMON_SERVICE_NAME": COMMON_SERVICE_NAME,
            "CLIENT_NAME": CLIENT_NAME,
            "TEST_STATUS": TEST_STATUS,
        }

        logger.confirm_continue()

        client = docker.from_env()
        services = client.services.list(filters={"name": SERVICE_NAME})
        if len(services) > 0:
            services[0].remove()
        self.CREATE(
            IMAGE_NAME=IMAGE_NAME,
            HOST_NAME=HOST_NAME,
            SERVICE_NAME=SERVICE_NAME,
            ENV_VARS=ENV_VARS,
            COMMON_SERVICE_NAME=COMMON_SERVICE_NAME,
            CLIENT_NAME=CLIENT_NAME,
            TEST_STATUS=TEST_STATUS,
        )

    def CREATE(self,
            IMAGE_NAME=None,
            HOST_NAME=None,
            SERVICE_NAME=None,
            ENV_VARS={},
            COMMON_SERVICE_NAME=None,
            CLIENT_NAME=None,
            TEST_STATUS="NOT_IN_TEST",
        ):
        logger.debug("Creating service '%s' for client '%s'" % (
            COMMON_SERVICE_NAME,CLIENT_NAME))
        logger.warning("\tIMAGE_NAME: %s" % IMAGE_NAME)
        logger.warning("\tHOST_NAME: %s" % HOST_NAME)
        logger.warning("\tSERVICE_NAME: %s" % SERVICE_NAME)
        logger.warning("\tENV_VARS: %s" % ENV_VARS)
        logger.warning("\tCOMMON_SERVICE_NAME: %s" % COMMON_SERVICE_NAME)
        logger.warning("\tCLIENT_NAME: %s" % CLIENT_NAME)
        logger.warning("\tTEST_STATUS: %s" % TEST_STATUS)

        info_dict = {
            "IMAGE_NAME": IMAGE_NAME,
            "HOST_NAME": HOST_NAME,
            "SERVICE_NAME": SERVICE_NAME,
            "ENV_VARS": ENV_VARS,
            "COMMON_SERVICE_NAME": COMMON_SERVICE_NAME,
            "CLIENT_NAME": CLIENT_NAME,
            "TEST_STATUS": TEST_STATUS,
        }

        NETWORKS = [
            "traefik-net",
        ]
        LABELS = {
            "traefik.enable": "true",
            "traefik.port": "80",
            "traefik.frontend.rule": "Host:%s" % HOST_NAME,
        }

        logger.confirm_continue()
        try:
            client = docker.from_env()
            client = client.services.create(
                image = IMAGE_NAME,
                name = SERVICE_NAME,
                env = ENV_VARS,

                networks = NETWORKS,
                labels = LABELS,
            )
            logger.success("Successfully created service '%s'" % SERVICE_NAME)
        except Exception as ex:
            logger.error("Failed to create service '%s': %s" % (
                SERVICE_NAME,
                str(es),
            ))

        self._data[SERVICE_NAME] = info_dict
        self._save()
