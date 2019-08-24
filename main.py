import yaml
import pyaml
import json
from rs_utils import logger

class ImageStore:

    _data = {}

    def __init__(self):
        self._load()

    def _dump(self):
        logger.debug("Local Images", line=True)
        data_str = json.dumps(self._data, indent=4)
        logger.debug(data_str)

    def _load(self):
        with open(self._config_location, "r") as file:
            self._data = json.load(file)

    def _save(self):
        with open(self._config_location, "w") as file:
            file.write(
                json.dumps(
                    self._data,
                    indent=4
                )
            )

class LocalImages(ImageStore):

    _config_location = "./LOCAL_IMAGES.json"

    def __init__(self):
        super(self.__class__, self).__init__()

    def BUILD(self, REPOSITORY=None, TAG=None):

        image_id = REPOSITORY + ":" + TAG
        error = False

        self._data[image_id] = error

        self._save()

    def PUSH(self, REPOSITORY=None, TAG=None):

        image_id = REPOSITORY + ":" + TAG

"""
local_images = LocalImages()
local_images._dump()
local_images.BUILD(
    REPOSITORY="rowsheet/hello_flask",
    TAG="latest")
local_images.BUILD(
    REPOSITORY="rowsheet/db_proxy",
    TAG="latest")
local_images.BUILD(
    REPOSITORY="rowsheet/database",
    TAG="latest")
local_images._save()
local_images._dump()
"""

class RemoteImages(ImageStore):

    _config_location = "./LOCAL_IMAGES.json"

    def __init__(self):
        super(self.__class__, self).__init__()

    def PUSH(self, REPOSITORY=None, TAG=None):

        image_id = REPOSITORY + ":" + TAG
        error = False

        self._data[image_id] = error

        self._save()

def TEMP_DEBUG(data, how="pprint"):
    if how == "json":
        data_str = json.dumps(data, indent=4)
        logger.debug("JSON DUMP", line=True)
        logger.debug(data_str)
    elif how == "yaml":
        data_str = pyaml.dump(data)
        logger.debug("YAML DUMP", line=True)
        logger.debug(data_str)
    else:
        import pprint
        data_str = pprint.pformat(data)
        logger.debug("PPRINT", line=True)
        logger.debug(data_str)

class ServiceConfig:

    _config_location = "./SERVICE_CONFIG.yaml"
    _distinct_tagged_images = []

    _config = None

    def __init__(self):
        self._load()

    def _dump(self):
        logger.debug("Service Config", line=True)
        config_str = pyaml.dump(self._config)
        logger.debug(config_str)

    def _load(self):
        with open(self._config_location, "r") as file:
            self._config = yaml.safe_load(file)
        self._load_distinct_tagged_images()
        self._validate_client_configs()

    def _validate_client_configs(self):
        clients = self._config["clients"]
        for client_name, client_config in clients.items():
            client_deployment = client_config["deployment"]
            deployment_services = list(
                self._config["deployments"][client_deployment]["services"]
            )
            deployment_services.sort()
            client_services = list(client_config["services"])
            client_services.sort()
            if deployment_services != client_services:
                raise Exception(("Invalid client '%s', deployment of " +
                    "type '%s', but missing some required services.") % (
                    client_name, client_deployment))
            client_services = client_config["services"]
            for client_service_name, client_service_config in client_services.items():
                dep_serv_req = self._config["services"][client_service_name]
                for env_name, env_required in dep_serv_req.items():
                    if env_required == True:
                        if env_name not in client_service_config:
                            raise Exception(("Invalid client service config for " +
                                "service '%s' for client '%s' is missing some " +
                                "required env_vars.") % (client_service_name, client_name))
                                

    def _load_distinct_tagged_images(self):
        deployments = self._config["deployments"]
        for deployment_name, deployment in deployments.items():
            services = deployment["services"]
            for service_name, service in services.items():
                prod_config = service["prod"]
                tagged_image = ":".join([
                    prod_config["repository"],
                    prod_config["tag"],
                ])
                self._distinct_tagged_images.append(tagged_image)
                stage_config = service["stage"]
                tagged_image = ":".join([
                    stage_config["repository"],
                    stage_config["tag"],
                ])
                self._distinct_tagged_images.append(tagged_image)
        self._distinct_tagged_images = set(self._distinct_tagged_images)
        # TEMP_DEBUG(self._distinct_tagged_images)

    def _save(self):
        with open(self._config_location, "w") as file:
            file.write(
                pyaml.dump(self._config)
            )

# service_config = ServiceConfig()
# service_config._dump()
# service_config._save()

#-------------------------------------------------------------------------------
# Step 0) Nothing is deployed anywhere.
#-------------------------------------------------------------------------------

def DEPLOY_FROM_CONFIG():
    service_config = ServiceConfig()

"""
#-------------------------------------------------------------------------------
# Step 1) “Latest” image built from last master commit ID (from commit_A)
#-------------------------------------------------------------------------------

def BUILD_LATEST_IMAGE_AS_LATEST(

#-------------------------------------------------------------------------------
# Step 2) “Latest” image pushed to dockerhub (from commit_A)
#-------------------------------------------------------------------------------

def PUSH_LATEST_IMAGE_AS_LATEST(

#-------------------------------------------------------------------------------
# Step 3) “Latest” image deployed to staging and vendor(s). Version routers point to “latest”.
#-------------------------------------------------------------------------------

def DEPLOY_LATEST_IMAGE_TO_STAGING(

def DEPLOY_LATEST_IMAGE_TO_CLIENT(
    CLIENT_NAME,

#-------------------------------------------------------------------------------
# Step 4) A new master branch is pushed to Github. This is detected with a registered web-hook.
#-------------------------------------------------------------------------------

def DETENCT_NOVEL_RELEASE_TAG(
    GIT_RELEASE_TAG,

#-------------------------------------------------------------------------------
# Step 5) The last “latest” image is tagged as “commit_A”, representing the codebase version it was running.
#-------------------------------------------------------------------------------

def TAG_LATEST_IMAGE_AS_LAGGING_RELEASE(
    GIT_RELEASE_TAG,

#-------------------------------------------------------------------------------
# Step 6) The newly tagged image (tagged from the last commit_id) is pushed to dockerhub.
#-------------------------------------------------------------------------------

def PUSH_LAGGING_IMAGE_AS_LAGGING_RELEASE(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 7) Vendor and staging configurations will be marked to use the tag “commit_A”.
#-------------------------------------------------------------------------------

def MARK_STAGING_CONFIG_AS_LAGGING_IMAGE(
    GIT_RELEASE_TAG

def MARK_CLIENT_CONFIG_AS_LAGGING_IMAGE(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 8) A new image tagged with “commit_B” will be built from the new master branch “commit_B”.
#-------------------------------------------------------------------------------

def BUILD_NOVEL_IMAGE_AS_NOVEL_TAG(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 9) The new image tagged “commit_B” will be deployed to staging.
#-------------------------------------------------------------------------------

def DEPLOY_NOVEL_IMAGE_TO_STAGING(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 11) Staging will be tested and either marked as 1) accepted or 2) rejected.
#-------------------------------------------------------------------------------

def FAIL_STAGING(

def PASS_STAGING(

#-------------------------------------------------------------------------------
# Step 12) If accepted, 1) the image tagged “commit_B” will be pushed to dockerhub. 
#-------------------------------------------------------------------------------

def PUSH_NOVEL_IMAGE_AS_NOVEL_TAG(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 13) If accepted, 2) the old staging image tagged “latest” is shut down.
#-------------------------------------------------------------------------------

def SHUTDOWN_STAGING_LATEST_IMAGE(

#-------------------------------------------------------------------------------
# Step 14) If accepted, 3) the staging configuration will be marked to use the image tagged with “commit_B”.
#-------------------------------------------------------------------------------

def MARK_STAGING_CONFIG_AS_NOVEL_IMAGE(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 15) If accepted, 4) the new image tagged “commit_B” will be deployed to vendors.
#-------------------------------------------------------------------------------

def DEPLOY_NOVEL_IMAGE_TO_CLIENT(

#-------------------------------------------------------------------------------
# Step 16) If accepted, 5) The version router on vendors will be set to point to the container tagged as “commit_B”.
#-------------------------------------------------------------------------------

def SHUTDOWN_CLIENT_LATEST_IMAGE(

#-------------------------------------------------------------------------------
# Step 17) If accepted, 6) the staging configuration will be marked to use the image tagged with “commit_B”.
#-------------------------------------------------------------------------------

def MARK_CLIENT_CONFIG_AS_NOVEL_IMAGE(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 18) If accepted and all vendors upgraded, the image tagged “commit_B” is tagged as “latest”.
#-------------------------------------------------------------------------------

def TAG_NOVEL_IMAGE_LATEST(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 19) If accepted and the “latest” image is now from “commit_B”, the “latest” image is pushed to dockerhub.
#-------------------------------------------------------------------------------

def PUSH_LATEST_IMAGE(

#-------------------------------------------------------------------------------
# Step 20) If accepted and the “latest” image has been pushed, staging and vendor configurations are marked to use “latest”.
#-------------------------------------------------------------------------------

def MARK_STAGING_CONFIG_AS_LATEST_IMAGE(

def MARK_CLIENT_CONFIG_AS_LATEST_IMAGE(
"""
