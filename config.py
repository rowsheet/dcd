import os

def DCD_DIR():
    return "/root/deploy/dcd"

def DCD_SERVICES_DIR():
    return os.path.join(DCD_DIR(), "services")

def DCD_DEPLOY_KEYS_DIR():
    return os.path.join(DCD_DIR(), "deploy_keys")

def DCD_OLD_CLONES_DIR():
    return os.path.join(DCD_SERVICES_DIR(), ".old")
