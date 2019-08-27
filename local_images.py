import json
import os

from rs_utils import logger
from rs_utils import runner
from rs_utils import timestamp
import config
from json_store import JsonStore

class LocalImages(JsonStore):

    _config_location = os.path.join(
        config.DCD_DIR(),
        "config",
        "LOCAL_IMAGES.json",
    )

    def __init__(self):
        super(self.__class__, self).__init__()

    def _image_guid(self, REGISTRY=None, TAG=None):
        return "%s:%s" % (REGISTRY, TAG)

    def _mark_image_action_response(self, image_guid, response, action):
        history = {}
        new_status = {}
        new_status["action"] = action
        if image_guid in self._data:
            last_status = self._data[image_guid]
            if "history" in last_status:
                history = last_status["history"]
                last_status.pop("history")
                history[timestamp.now()] = last_status
        new_status["error"] = response.ERROR
        new_status["error_msg"] = response.ERROR_MSG
        new_status["history"] = history
        self._data[image_guid] = new_status

    def TAG(self, REGISTRY=None, TAG_FROM=None, TAG_TO=None):
        image_guid_from = REGISTRY + ":" + TAG_FROM
        image_guid_to = REGISTRY + ":" + TAG_TO

        cmd = "docker tag %s %s" % (
            image_guid_from,
            image_guid_to,
        )
        response = runner.step(
            cmd,
            "Tagging image '%s' with lagging release '%s'" % (
                REGISTRY,
                TAG_TO,
            ),
            stdout_log = False,
        )
        image_guid = self._image_guid(
            REGISTRY=REGISTRY,
            TAG=TAG_TO,
        )
        self._mark_image_action_response(image_guid, response, "TAG")
        self._save()
        return self

    def BUILD(self, REPOSITORY=None, REGISTRY=None, TAG=None):
        repo_name = REPOSITORY.split("/")[1].split(".")[0]
        repo_path = os.path.join(config.DCD_SERVICES_DIR(), repo_name)
        image_guid = self._image_guid(
            REGISTRY=REGISTRY,
            TAG=TAG,
        )
        response = runner.step(
            "docker build -t %s %s" % (image_guid, repo_path),
            "Building image '%s'..." % image_guid,
            stdout_log = False,
        )
        self._mark_image_action_response(image_guid, response, "BUILD")
        self._save()
        return self

    def PUSH(self, REGISTRY=None, TAG=None):
        image_guid = self._image_guid(
            REGISTRY=REGISTRY,
            TAG=TAG,
        )
        response = runner.step(
            "docker push %s" % image_guid,
            "Pushing image '%s'..." % image_guid,
            stdout_log = False,
        )
        self._mark_image_action_response(image_guid, response, "PUSH")
        self._save()
        return self
