import yaml
import pyaml
import json
from rs_utils import logger

class JsonStore:

    _data = {}

    def __init__(self):
        self._load()

    def _dump(self):
        logger.debug("", line=True)
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

class LocalImages(JsonStore):

    _config_location = "./LOCAL_IMAGES.json"

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

class RemoteImages(JsonStore):

    _config_location = "./REMOTE_IMAGES.json"

    def __init__(self):
        super(self.__class__, self).__init__()

    def PUSH(self, IMAGE_GUID=None):
        logger.success("Remove recieving image '%s'..." % IMAGE_GUID)
        error = False
        self._data[IMAGE_GUID] = error
        self._save()

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
            deployment_services = self._config["deployments"][client_deployment]["services"]
            deployment_services.sort()
            client_services = list(client_config["services"])
            client_services.sort()
            if deployment_services != client_services:
                raise Exception(("Invalid client '%s', deployment of " +
                    "type '%s', but missing some required services.") % (
                    client_name, client_deployment))
            client_services = client_config["services"]
            for client_service_name, client_service_config in client_services.items():
                env_var_req = self._config["services"][client_service_name]["env_var_req"]
                for env_name, env_required in env_var_req.items():
                    if env_required == True:
                        if env_name not in client_service_config:
                            raise Exception(("Invalid client service config for " +
                                "service '%s' for client '%s' is missing some " +
                                "required env_vars.") % (client_service_name, client_name))
                                

    def _load_distinct_tagged_images(self):
        services = self._config["services"]
        for service_name, service in services.items():
            registry = service["registry"]
            repository = service["repository"]
            version_status = service["version_status"]
            tagged_image = ":".join([
                registry,
                version_status["prod"],
            ])
            self._distinct_tagged_images.append(tagged_image)
            tagged_image = ":".join([
                registry,
                version_status["stage"],
            ])
            self._distinct_tagged_images.append(tagged_image)
        self._distinct_tagged_images = set(self._distinct_tagged_images)

    def _save(self):
        with open(self._config_location, "w") as file:
            file.write(
                pyaml.dump(self._config)
            )

    def BUILD_ALL_LATEST_IMAGE_AS_LATEST(self):
        local_images = LocalImages()
        services = self._config["services"]
        for service_name, service_config in services.items():
            repository = service_config["repository"]
            registry = service_config["registry"]
            GITHUB_CLONE_OR_PULL(repository)
            local_images.BUILD(
                REGISTRY=registry,
                TAG="latest",
            )
            print("\n")

    def PUSH_ALL_LATEST_IMAGE_AS_LATEST(self):
        local_images = LocalImages()
        services = self._config["services"]
        for service_name, service_config in services.items():
            repository = service_config["repository"]
            registry = service_config["registry"]
            local_images.PUSH(
                REGISTRY=registry,
                TAG="latest",
            )

    def DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_CLIENTS(self):
        services = Services()
        clients = self._config["clients"]
        for client_name, client_config in clients.items():
            client_services = client_config["services"]
            for client_service_name, client_service_env_vars in client_services.items():
                registry = self._config["services"][client_service_name]["registry"]
                image_name = registry + ":latest"
                service_name = "--".join([
                    client_name,
                    client_service_name,
                ])
                host_name = ".".join([
                    client_name,
                    client_service_name,
                    "rowsheet.com",
                ]) 
                services.CREATE(
                    IMAGE_NAME=image_name,
                    HOST_NAME=host_name,
                    SERVICE_NAME=service_name,
                    ENV_VARS=client_service_env_vars,
                    COMMON_SERVICE_NAME=client_service_name,
                    CLIENT_NAME=client_name,
                )

def GITHUB_CLONE_OR_PULL(repository):
    logger.debug("Cloning or pulling repository '%s'" % repository)
    logger.warning("git clone %s" % repository)

class Services(JsonStore):

    _config_location = "./SERVICES.json"

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

#-------------------------------------------------------------------------------
# Step 0) Nothing is deployed anywhere.
#-------------------------------------------------------------------------------

service_config = ServiceConfig()

#-------------------------------------------------------------------------------
# Step 1) “Latest” image built from last master commit ID (from commit_A)
#-------------------------------------------------------------------------------

service_config.BUILD_ALL_LATEST_IMAGE_AS_LATEST()

#-------------------------------------------------------------------------------
# Step 2) “Latest” image pushed to dockerhub (from commit_A)
#-------------------------------------------------------------------------------

service_config.PUSH_ALL_LATEST_IMAGE_AS_LATEST()

#-------------------------------------------------------------------------------
# Step 3) “Latest” image deployed to staging and vendor(s). Version routers point to “latest”.
#-------------------------------------------------------------------------------

service_config.DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_CLIENTS()

"""

#-------------------------------------------------------------------------------
# Step 4) A new master branch is pushed to Github. This is detected with a registered web-hook.
#-------------------------------------------------------------------------------

def DETENCT_NOVEL_RELEASE_TAG(
    GIT_RELEASE_TAG,

"""

"""

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
