from enum import Enum
import docker
from rs_utils import logger
from rs_utils import runner

"""
def build_prod():
    client.services.create(
        image = 'rowsheet/hello-flask:latest',
        networks = [
            'traefik-net'
            ],
        labels = {
            'traefik.enable': 'true',
            'traefik.port': '80',
            'traefik.frontend.rule': 'Host:helloflask.alpinecover.com'
            },
        name = 'helloflask',
        env = [
            "HELLO_FLASK_PORT=80",
            "HELLO_FLASK_MESSAGE=Version 1.",
        ]
            )
"""


class RSException(Exception):
    MSG = None
    CODE = None
    def __init__(self,
            MSG = None,
            CODE = None,
        ):
        self.MSG = MSG
        if self.MSG is None:
            self.MSG = "No message provided."
        self.CODE = CODE
        if self.CODE is None:
            self.CODE = RSException_CODES.NO_CODE_PROVIDED

class RSException_CODES(Enum):
    NO_CODE = 0
    SERVICE_DOESNT_EXIST = 1

client = docker.from_env()

def load_service_ids_by_name():
    logger.debug("load_service_ids_by_name:")

    #---------------------------------------------------------------------------
    # logger.confirm_continue()
    #---------------------------------------------------------------------------

    services = client.services.list()
    return {
        service.name: service.id
        for service in services
    }

def load_service_by_name(service_name):
    logger.debug("load_service_by_name: '%s'" % service_name)

    #---------------------------------------------------------------------------
    # logger.confirm_continue()
    #---------------------------------------------------------------------------

    service_ids_by_name = load_service_ids_by_name()
    if service_name in service_ids_by_name:
        service_id = service_ids_by_name[service_name]
        service = client.services.get(
            service_id = service_id
        )
        return service
    raise RSException(
            MSG     = "No ervice with name '%s' exists" % service_name,
            CODE    = RSException_CODES.SERVICE_DOESNT_EXIST
        )

"""
def remove_image(image_name):
    logger.debug("remove_image: '%s'" % image_name)
"""

def build_image(repo_name, image_name):
    logger.debug("build_image: '%s','%s'" % (repo_name, image_name))

    #---------------------------------------------------------------------------
    # logger.confirm_continue()
    #---------------------------------------------------------------------------

    runner.step(
        "docker build -t %s ./services/%s" % (image_name, repo_name),
        "Re-building dev image."
    )

def remove_service(service_name):
    logger.debug("remove_service: '%s'" % service_name)

    #---------------------------------------------------------------------------
    # logger.confirm_continue()
    #---------------------------------------------------------------------------

    try:
        service = load_service_by_name(service_name)
        service.remove()
    except RSException as rs_ex:
        if rs_ex.CODE != RSException_CODES.SERVICE_DOESNT_EXIST:
            raise Exception(str(RSException))
    except Exception as ex:
        raise Exception(str(ex))

def launch_service(service_name, image_name, host_name):
    logger.debug("launch_service: '%s','%s','%s'" % (
        service_name, image_name, host_name
    ))

    #---------------------------------------------------------------------------
    # logger.confirm_continue()
    #---------------------------------------------------------------------------

    remove_service(service_name)
    client.services.create(
        image = image_name,
        networks = [
            'traefik-net'
            ],
        labels = {
            'traefik.enable': 'true',
            'traefik.port': '80',
            'traefik.frontend.rule': 'Host:%s' % host_name
            },
        name = service_name,
        env = [
            "HELLO_FLASK_PORT=8000",
            "HELLO_FLASK_MESSAGE=Dev Version 3.",
        ]
            )

def clean_for_host_name(name):
    return name.replace("_","-").lower()

def clean_for_service_name(name):
    return name.replace(".","-").lower()

def build_host_name(client, repo_name, right_level_domain):
    return ".".join([
        clean_for_host_name(client),
        clean_for_host_name(repo_name),
        clean_for_host_name(right_level_domain),
    ])

def build_service_name(client, repo_name, right_level_domain):
    return "--".join([
        clean_for_service_name(client),
        clean_for_service_name(repo_name),
        clean_for_service_name(right_level_domain),
    ])

def build_image_name(docker_registry_base_path, repo_name, tag):
    return "%s/%s:%s" % (
        docker_registry_base_path,
        repo_name,
        tag,
    )

def LAUNCH_DEV(repo_name, right_level_domain, docker_registry_base_path):
    logger.debug("launch_latest_dev: '%s'" % repo_name)
    """ host_name """
    host_name = build_host_name(
        "dev", repo_name, right_level_domain
    )
    logger.warning("\thost_name: '%s'" % host_name)
    """ image_name """
    image_name = build_image_name(
        docker_registry_base_path,
        repo_name,
        "dev",
    )
    logger.warning("\timage_name: '%s'" % image_name)
    """ service_name """
    service_name = build_service_name(
        "dev", repo_name, right_level_domain
    )
    logger.warning("\tservice_name: '%s'" % service_name)

    #---------------------------------------------------------------------------
    # logger.confirm_continue()
    #---------------------------------------------------------------------------

    build_image(repo_name, image_name)
    launch_service(service_name, image_name, host_name)

# logger.confirm_continue()
LAUNCH_DEV("hello_flask", "rowsheet.com", "rowsheet")
