import yaml
import pyaml
import os

from rs_utils import logger
from rs_utils import runner
from rs_utils import timestamp 
import config
from local_images import LocalImages
from services import Services

class ServiceConfig:

    _config_location = os.path.join(
        config.DCD_DIR(),
        "config",
        "SERVICE_CONFIG.yaml",
    )

    _distinct_tagged_images = []

    _config = None

    #---------------------------------------------------------------------------
    # PUBLIC
    #---------------------------------------------------------------------------

    def __init__(self):
        self._load()

    def LAUNCH_FROM_CONFIG(self):
        logger.warning("BUILD_ALL_LATEST_IMAGE_AS_LATEST", line=True)
        logger.confirm_continue()
        self._BUILD_ALL_LATEST_IMAGE_AS_LATEST()
        logger.warning("PUSH_ALL_LATEST_IMAGE_AS_LATEST", line=True)
        logger.confirm_continue()
        self._PUSH_ALL_LATEST_IMAGE_AS_LATEST()
        logger.warning("DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_PRODUCTION", line=True)
        logger.confirm_continue()
        self._DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_PRODUCTION()

    def DETENCT_NOVEL_RELEASE_TAG(self, repository, novel_tag):
        logger.warning("TAG_AND_PUSH_LATEST_IMAGE_AS_LAGGING_RELEASE", line=True)
        logger.confirm_continue()
        self._TAG_AND_PUSH_LATEST_IMAGE_AS_LAGGING_RELEASE(repository)
        logger.warning("MARK_STAGING_CONFIG_AS_LAGGING_IMAGE", line=True)
        logger.confirm_continue()
        self._MARK_STAGING_CONFIG_AS_LAGGING_IMAGE(repository)
        logger.warning("MARK_PRODUCTION_CONFIG_AS_LAGGING_IMAGE", line=True)
        logger.confirm_continue()
        self._MARK_PRODUCTION_CONFIG_AS_LAGGING_IMAGE(repository)
        logger.warning("BUILD_NOVEL_IMAGE_AS_NOVEL_TAG", line=True)
        logger.confirm_continue()
        self._BUILD_NOVEL_IMAGE_AS_NOVEL_TAG(repository, novel_tag)
        logger.warning("DEPLOY_NOVEL_IMAGE_TO_STAGING", line=True)
        logger.confirm_continue()
        self._DEPLOY_NOVEL_IMAGE_TO_STAGING(repository, novel_tag)

    def PASS_STAGING(self, repository, novel_tag):
        logger.warning("PUSH_NOVEL_IMAGE_AS_NOVEL_TAG", line=True)
        logger.confirm_continue()
        self._PUSH_NOVEL_IMAGE_AS_NOVEL_TAG(repository, novel_tag)
        logger.warning("MARK_STAGING_CONFIG_AS_NOVEL_IMAGE", line=True)
        logger.confirm_continue()
        self._MARK_STAGING_CONFIG_AS_NOVEL_IMAGE(repository, novel_tag)
        logger.warning("DEPLOY_NOVEL_IMAGE_TO_PRODUCTION", line=True)
        logger.confirm_continue()
        self._DEPLOY_NOVEL_IMAGE_TO_PRODUCTION(repository, novel_tag)
        logger.warning("MARK_PRODUCTION_CONFIG_AS_NOVEL_IMAGE", line=True)
        logger.confirm_continue()
        self._MARK_PRODUCTION_CONFIG_AS_NOVEL_IMAGE(repository, novel_tag)
        logger.warning("TAG_AND_PUSH_NOVEL_IMAGE_AS_LATEST", line=True)
        logger.confirm_continue()
        self._TAG_AND_PUSH_NOVEL_IMAGE_AS_LATEST(repository, novel_tag)
        logger.warning("MARK_STAGING_CONFIG_AS_LATEST", line=True)
        logger.confirm_continue()
        self._MARK_STAGING_CONFIG_AS_LATEST(repository)
        logger.warning("MARK_PRODUCTION_CONFIG_AS_LATEST", line=True)
        logger.confirm_continue()
        self._MARK_PRODUCTION_CONFIG_AS_LATEST(repository)
        logger.warning("MARK_STAGING_SERVICES_PASSED", line=True)
        logger.confirm_continue()
        self._MARK_STAGING_SERVICES_PASSED(repository, novel_tag)

    #---------------------------------------------------------------------------
    # PRIVATE:
    #   Initialization
    #---------------------------------------------------------------------------

    """
    def _dump(self):
        logger.debug("Service Config", line=True)
        config_str = pyaml.dump(self._config)
        logger.debug(config_str)
    """

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
        config_filepath = self._config_location
        backup_config_filepath = "%s.backup_%s" % (
            self._config_location,
            timestamp.now().replace(" ","_"),
        )
        os.system("cp %s %s" % (
            config_filepath,
            backup_config_filepath))
        try:
            with open(self._config_location, "w") as file:
                file.write(
                    pyaml.dump(self._config)
                )
        except Exception as ex:
            logger.error("Failed to save %s, backup file at %s." % (
                config_filepath,
                backup_config_filepath))
            logger.error("\t" + str(ex))
            return
        os.system("rm %s" % backup_config_filepath)

    #---------------------------------------------------------------------------
    # PRIVATE:
    #   LAUNCH_FROM_CONFIG 
    #---------------------------------------------------------------------------

    def _BUILD_ALL_LATEST_IMAGE_AS_LATEST(self):
        local_images = LocalImages()
        services = self._config["services"]
        for service_name, service_config in services.items():
            repository = service_config["repository"]
            registry = service_config["registry"]
            self._github_clone(repository)
            local_images.BUILD(
                REPOSITORY=repository,
                REGISTRY=registry,
                TAG="latest",
            )
            print("\n")

    def _PUSH_ALL_LATEST_IMAGE_AS_LATEST(self):
        local_images = LocalImages()
        services = self._config["services"]
        for service_name, service_config in services.items():
            repository = service_config["repository"]
            registry = service_config["registry"]
            local_images.PUSH(
                REGISTRY=registry,
                TAG="latest",
            )

    def _DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_PRODUCTION(self):
        services = Services()
        clients = self._config["clients"]
        for client_name, client_config in clients.items():
            client_services = client_config["services"]
            for client_service_name, client_service_env_vars in client_services.items():
                registry = self._config["services"][client_service_name]["registry"]
                tldn = self._config["services"][client_service_name]["tldn"]
                service_subdomain = self._config["services"][client_service_name]["service_subdomain"]
                image_name = registry + ":latest"
                service_name = self._build_docker_service_name(
                    client_name,
                    service_subdomain,
                    tldn,
                )
                host_name = self._build_hostname(
                    client_name,
                    service_subdomain,
                    tldn,
                )
                services.DELETE(
                    SERVICE_NAME=service_name,
                ).CREATE(
                    IMAGE_NAME=image_name,
                    HOST_NAME=host_name,
                    SERVICE_NAME=service_name,
                    ENV_VARS=client_service_env_vars,
                    COMMON_SERVICE_NAME=client_service_name,
                    CLIENT_NAME=client_name,
                )

    #---------------------------------------------------------------------------
    # PRIVATE:
    #   DETENCT_NOVEL_RELEASE_TAG
    #---------------------------------------------------------------------------

    def _TAG_AND_PUSH_LATEST_IMAGE_AS_LAGGING_RELEASE(self, repository):
        self._github_clone(repository)
        last_tag = self._get_last_tag(repository)
        registry = self._get_registry(repository)

        local_images = LocalImages()

        local_images.TAG(
            REGISTRY=registry,
            TAG_FROM="latest",
            TAG_TO=last_tag,
        ).PUSH(
            REGISTRY=registry,
            TAG=last_tag,
        )

    def _MARK_STAGING_CONFIG_AS_LAGGING_IMAGE(self, repository):
        service_name = self._get_service_name(repository)
        last_tag = self._get_last_tag(repository)

        self._config["services"][service_name]["version_status"]["stage"] = last_tag
        self._save()

    def _MARK_PRODUCTION_CONFIG_AS_LAGGING_IMAGE(self, repository):
        service_name = self._get_service_name(repository)
        last_tag = self._get_last_tag(repository)

        self._config["services"][service_name]["version_status"]["prod"] = last_tag
        self._save()

    def _BUILD_NOVEL_IMAGE_AS_NOVEL_TAG(self, repository, novel_tag):
        repo_name = self._build_repo_name(repository)
        repo_path = self._build_repo_path(repository)
        registry = self._get_registry(repository)

        self._github_clone(repository)
        response = runner.step(
            "cd %s && git checkout %s" % (repo_path, novel_tag),
            "Checking out tag '%s' for repo '%s'" % (novel_tag, repo_name),
        )
        if response.ERROR == True:
            raise Exception("Error checking out tag '%s' for repo '%s'" % (
                novel_tag,
                repo_name,
            ))

        local_images = LocalImages()
        local_images.BUILD(
            REPOSITORY=repository,
            REGISTRY=registry,
            TAG=novel_tag,
        )
        print("\n")

    def _DEPLOY_NOVEL_IMAGE_TO_STAGING(self, repository, novel_tag):
        registry = self._get_registry(repository)
        service_name = self._get_service_name(repository)

        staging_clients_with_service = {}
        staging_client_names_with_service = self._get_staging_clients_with_service(service_name)
        for client_name in staging_client_names_with_service:
            service_subdomain = self._config["services"][service_name]["service_subdomain"]
            tldn = self._config["services"][service_name]["tldn"]
            client_service_name = self._build_docker_service_name(
                client_name,
                service_subdomain,
                tldn,
            )
            novel_image_guid = registry + ":" + novel_tag
            host_name = self._build_hostname(
                client_name,
                service_subdomain,
                tldn,
            )
            client_services = self._config["clients"][client_name]["services"]
            client_service_env_vars = client_services[service_name]
            staging_client_service_info = {
                "IMAGE_NAME": novel_image_guid,
                "HOST_NAME": host_name,
                "SERVICE_NAME": client_service_name,
                "ENV_VARS": client_service_env_vars,
                "COMMON_SERVICE_NAME": service_name,
                "CLIENT_NAME": client_name,
            }
            staging_clients_with_service[client_name] = staging_client_service_info

        services = Services()
        for staging_client_name, config in staging_clients_with_service.items():
            services.UPGRADE(**config)

    #---------------------------------------------------------------------------
    # PRIVATE:
    #   PASS_STAGING
    #---------------------------------------------------------------------------

    def _PUSH_NOVEL_IMAGE_AS_NOVEL_TAG(self, repository, novel_tag):
        registry = self._get_registry(repository)

        local_images = LocalImages()

        local_images.PUSH(
            REGISTRY=registry,
            TAG=novel_tag,
        )

    def _MARK_STAGING_CONFIG_AS_NOVEL_IMAGE(self, repository, novel_tag):
        service_name = self._get_service_name(repository)

        self._config["services"][service_name]["version_status"]["stage"] = novel_tag
        self._save()

    def _DEPLOY_NOVEL_IMAGE_TO_PRODUCTION(self, repository, novel_tag):
        registry = self._get_registry(repository)
        service_name = self._get_service_name(repository)

        prod_clients_with_service = {}
        prod_client_names_with_service = self._get_production_clients_with_service(service_name)
        for client_name in prod_client_names_with_service:
            service_subdomain = self._config["services"][service_name]["service_subdomain"]
            tldn = self._config["services"][service_name]["tldn"]
            client_service_name = self._build_docker_service_name(
                client_name,
                service_subdomain,
                tldn,
            )
            novel_image_guid = registry + ":" + novel_tag
            host_name = self._build_hostname(
                client_name,
                service_subdomain,
                tldn,
            )
            client_services = self._config["clients"][client_name]["services"]
            client_service_env_vars = client_services[service_name]
            prod_client_service_info = {
                "IMAGE_NAME": novel_image_guid,
                "HOST_NAME": host_name,
                "SERVICE_NAME": client_service_name,
                "ENV_VARS": client_service_env_vars,
                "COMMON_SERVICE_NAME": service_name,
                "CLIENT_NAME": client_name,
            }
            prod_clients_with_service[client_name] = prod_client_service_info

        services = Services()
        for prod_client_name, config in prod_clients_with_service.items():
            config["TEST_STATUS"] = "NOT_IN_TEST"
            services.UPGRADE(**config)

    def _MARK_PRODUCTION_CONFIG_AS_NOVEL_IMAGE(self, repository, novel_tag):
        service_name = self._get_service_name(repository)

        self._config["services"][service_name]["version_status"]["prod"] = novel_tag
        self._save()

    def _TAG_AND_PUSH_NOVEL_IMAGE_AS_LATEST(self, repository, novel_tag):
        # self._github_clone(repository)
        registry = self._get_registry(repository)

        local_images = LocalImages()

        local_images.TAG(
            REGISTRY=registry,
            TAG_FROM=novel_tag,
            TAG_TO="latest",
        ).PUSH(
            REGISTRY=registry,
            TAG="latest",
        )

    def _MARK_STAGING_CONFIG_AS_LATEST(self, repository):
        service_name = self._get_service_name(repository)

        self._config["services"][service_name]["version_status"]["stage"] = "latest"
        self._save()

    def _MARK_PRODUCTION_CONFIG_AS_LATEST(self, repository):
        service_name = self._get_service_name(repository)

        self._config["services"][service_name]["version_status"]["prod"] = "latest"
        self._save()

    def _MARK_STAGING_SERVICES_PASSED(self, repository, novel_tag):
        service_name = self._get_service_name(repository)
        staging_clients_with_service = self._get_staging_clients_with_service(service_name)
        logger.warning(staging_clients_with_service)
        services = Services()
        for client_name in staging_clients_with_service:
            service_subdomain = self._config["services"][service_name]["service_subdomain"]
            tldn = self._config["services"][service_name]["tldn"]
            client_service_name = self._build_docker_service_name(
                client_name,
                service_subdomain,
                tldn,
            )
            services.MARK_TEST_PASSED(
                SERVICE_NAME=client_service_name,
            )

    #---------------------------------------------------------------------------
    # PRIVATE:
    #   Helper Methods
    #---------------------------------------------------------------------------

    def _build_docker_service_name(self, client_name, service_subdomain, tldn):
        return ("%s--%s--%s" % (
            service_subdomain,
            client_name,
            tldn.replace(".","--dot--"),
        )).replace("_","-").replace(".","--").replace(" ","").strip("--").lower()

    def _build_hostname(self, client_name, service_subdomain, tldn):
        return ("%s.%s.%s" % (
            service_subdomain,
            client_name,
            tldn,
        )).replace("_","-").replace(" ","").replace("..",".").strip(".").lower()

    def _build_repo_path(self, repository):
        repo_name = self._build_repo_name(repository)
        return os.path.join(config.DCD_SERVICES_DIR(), repo_name, "")

    def _build_repo_name(self, repository):
        return repository.split("/")[1].split(".")[0]

    def _build_deploy_key_path(self, repository):
        repo_name = self._build_repo_name(repository)
        return os.path.join(config.DCD_DEPLOY_KEYS_DIR(), repo_name)

    def _get_last_tag(self, repository):
        repo_path = self._build_repo_path(repository)

        response = runner.step(
            "cd %s && git tag" % repo_path,
            "Getting tags...",
        )

        if response.ERROR == True:
            raise Exception("Unable to get git tags.")

        tags = list(filter(lambda tag: tag != "", response.STDOUT.split("\n")))
        logger.warning(tags)
        if len(tags) == 0:
            last_tag = "start"
        elif len(tags) == 1:
            last_tag = "v0.0.0"
        else:
            last_tag = tags[-2]
        return last_tag

    def _get_registry(self, repository):
        target_service = None
        for service_name, service in self._config["services"].items():
            if service["repository"] == repository:
                target_service = service
                break
        registry = target_service["registry"]
        return registry

    def _get_service_name(self, repository):
        target_service_name = None
        for service_name, service in self._config["services"].items():
            if service["repository"] == repository:
                target_service_name = service_name
                break
        return target_service_name

    def _get_production_clients_with_service(self, service_name):
        client_names = []
        for client_name, client in self._config["clients"].items():
            if client["type"] == "prod":
                client_services = client["services"]
                if service_name in client_services:
                    client_names.append(client_name)
        return client_names

    def _get_staging_clients_with_service(self, service_name):
        client_names = []
        for client_name, client in self._config["clients"].items():
            if client["type"] == "staging":
                client_services = client["services"]
                if service_name in client_services:
                    client_names.append(client_name)
        return client_names

    def _github_clone(self, repository):
        repo_name = self._build_repo_name(repository)
        repo_path = self._build_repo_path(repository)
        deploy_key_path = self._build_deploy_key_path(repository)

        if os.path.isdir(config.DCD_OLD_CLONES_DIR()) == False:
            os.system("mkdir %s" % config.DCD_OLD_CLONES_DIR())
        file_timestamp = timestamp.now().replace(" ","_")
        mv_old_cmd = "mv %s %s%s" % (
                repo_path,
                os.path.join(config.DCD_OLD_CLONES_DIR(), repo_name),
                file_timestamp
        )
        response = runner.step(
            mv_old_cmd,
            "Moving old repos to archive dir."
        )

        clone_cmd = "ssh-agent bash -c 'ssh-add %s; git clone git@%s %s'" % (
            deploy_key_path,
            repository,
            repo_path,
        )
        response = runner.step(
            clone_cmd,
            "Cloning or pulling repository '%s'" % repository
        )
