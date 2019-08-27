import yaml
import pyaml
import json
from os import path

from rs_utils import logger
import config
from json_store import JsonStore
from local_images import LocalImages
from remote_images import RemoteImages
from service_config import ServiceConfig
from services import Services

#-------------------------------------------------------------------------------
# Step 0) Nothing is deployed anywhere.
#-------------------------------------------------------------------------------

service_config = ServiceConfig()

#-------------------------------------------------------------------------------
# Step 1) “Latest” image built from last master commit ID (from commit_A)
#-------------------------------------------------------------------------------

"""

service_config.BUILD_ALL_LATEST_IMAGE_AS_LATEST()

#-------------------------------------------------------------------------------
# Step 2) “Latest” image pushed to dockerhub (from commit_A)
#-------------------------------------------------------------------------------

service_config.PUSH_ALL_LATEST_IMAGE_AS_LATEST()

#-------------------------------------------------------------------------------
# Step 3) “Latest” image deployed to staging and vendor(s). Version routers point to “latest”.
#-------------------------------------------------------------------------------

service_config.DEPLOY_ALL_LATEST_IMAGE_TO_STAGING_AND_PRODUCTION()


#-------------------------------------------------------------------------------
# Step 4) A new master branch is pushed to Github. This is detected with a registered web-hook.
#-------------------------------------------------------------------------------

def DETENCT_NOVEL_RELEASE_TAG(
    GIT_RELEASE_TAG,



#-------------------------------------------------------------------------------
# Step 5) The last “latest” image is tagged as “commit_A”, representing the codebase version it was running.
# Step 6) The newly tagged image (tagged from the last commit_id) is pushed to dockerhub.
#-------------------------------------------------------------------------------

service_config.TAG_AND_PUSH_LATEST_IMAGE_AS_LAGGING_RELEASE("github.com:rowsheet/fake_analytics.git")

#-------------------------------------------------------------------------------
# Step 7) Vendor and staging configurations will be marked to use the tag “commit_A”.
#-------------------------------------------------------------------------------

service_config.MARK_STAGING_CONFIG_AS_LAGGING_IMAGE("github.com:rowsheet/fake_analytics.git")

service_config.MARK_PRODUCTION_CONFIG_AS_LAGGING_IMAGE("github.com:rowsheet/fake_analytics.git")

#-------------------------------------------------------------------------------
# Step 8) A new image tagged with “commit_B” will be built from the new master branch “commit_B”.
#-------------------------------------------------------------------------------

service_config.BUILD_NOVEL_IMAGE_AS_NOVEL_TAG(
    "github.com:rowsheet/fake_analytics.git",
    "v0.0.4",
)

#-------------------------------------------------------------------------------
# Step 9) The new image tagged “commit_B” will be deployed to staging.
#-------------------------------------------------------------------------------

service_config.DEPLOY_NOVEL_IMAGE_TO_STAGING(
    "github.com:rowsheet/fake_analytics.git",
    "v0.0.4",
)

#-------------------------------------------------------------------------------
# Step 11) Staging will be tested and either marked as 1) accepted or 2) rejected.
#-------------------------------------------------------------------------------

def FAIL_STAGING(
"""

service_config.PASS_STAGING(
    "github.com:rowsheet/fake_analytics.git",
    "v0.0.4",
)

#-------------------------------------------------------------------------------
# Step 12) If accepted, 1) the image tagged “commit_B” will be pushed to dockerhub. 
#-------------------------------------------------------------------------------

# def PUSH_NOVEL_IMAGE_AS_NOVEL_TAG(
#     GIT_RELEASE_TAG

"""
#-------------------------------------------------------------------------------
# Step 14) If accepted, 3) the staging configuration will be marked to use the image tagged with “commit_B”.
#-------------------------------------------------------------------------------

def MARK_STAGING_CONFIG_AS_NOVEL_IMAGE(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 15) If accepted, 4) the new image tagged “commit_B” will be deployed to vendors.
#-------------------------------------------------------------------------------

def DEPLOY_NOVEL_IMAGE_TO_PRODUCTION(

#-------------------------------------------------------------------------------
# Step 16) If accepted, 5) The version router on vendors will be set to point to the container tagged as “commit_B”.
#-------------------------------------------------------------------------------

def REMOVE_LATEST_IMAGE(

#-------------------------------------------------------------------------------
# Step 17) If accepted, 6) the staging configuration will be marked to use the image tagged with “commit_B”.
#-------------------------------------------------------------------------------

def MARK_PRODUCTION_CONFIG_AS_NOVEL_IMAGE(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 18) If accepted and all vendors upgraded, the image tagged “commit_B” is tagged as “latest”.
# Step 19) If accepted and the “latest” image is now from “commit_B”, the “latest” image is pushed to dockerhub.
#-------------------------------------------------------------------------------

def TAG_AND_PUSH_NOVEL_IMAGE_AS_LATEST(
    GIT_RELEASE_TAG

#-------------------------------------------------------------------------------
# Step 20) If accepted and the “latest” image has been pushed, staging and vendor configurations are marked to use “latest”.
#-------------------------------------------------------------------------------

def MARK_STAGING_CONFIG_AS_LATEST_IMAGE(

def MARK_PRODUCTION_CONFIG_AS_LATEST_IMAGE(
"""
