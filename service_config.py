import yaml
import pyaml
import os
import docker

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

    def BUILD_ALL_LATEST_IMAGE_AS_LATEST(self):
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

    def DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_CLIENTS(self):
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
                )
                services.CREATE(
                    IMAGE_NAME=image_name,
                    HOST_NAME=host_name,
                    SERVICE_NAME=service_name,
                    ENV_VARS=client_service_env_vars,
                    COMMON_SERVICE_NAME=client_service_name,
                    CLIENT_NAME=client_name,
                )

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

    def TAG_AND_PUSH_LATEST_IMAGE_AS_LAGGING_RELEASE(self, repository):
        self._github_clone(repository)
        last_tag = self._get_last_tag(repository)
        registry = self._get_registry(repository)

        image_guid_from = registry + ":latest"
        image_guid_to = registry + ":" + last_tag

        cmd = "docker tag %s %s" % (
            image_guid_from,
            image_guid_to,
        )
        response = runner.step(
            cmd,
            "Tagging image '%s' with lagging release '%s'" % (
                registry,
                last_tag,
            ),
            stdout_log = False,
        )
        if response.ERROR == True:
            raise Exception("Error tagging image with lagging relase: %s" %
                response.STDERR)

        cmd = "docker push %s" % image_guid_to
        response = runner.step(
            cmd,
            "Pushing image '%s' with lagging release '%s'" % (
                registry,
                last_tag,
            ),
            stdout_log = False,
        )
        if response.ERROR == True:
            raise Exception("Error pushing lagging relase image '%s': %s" % (
                image_guid_to,
                response.STDERR,
            ))

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
