import docker
import os

# Make sure "acme.json" exists as an empty file with permissions set to 600.
if os.path.exists("./acme.json") == True:
    os.system("mv ./acme.json ./acme.json.old")
os.system("touch ./acme.json")
os.system("chmod 600 ./acme.json")
        
client = docker.from_env()

# Create the traefik network.
client.networks.create(
    name = 'traefik-net',
    driver = 'overlay'
        )

# Create the traefik service.
client.services.create(
    image = 'traefik:alpine',
    name = 'traefik',
    mounts = [
        '/var/run/docker.sock:/var/run/docker.sock',
        os.getcwd() + '/traefik.toml:/etc/traefik/traefik.toml',
        os.getcwd() + '/acme.json:/acme.json'
        ],
    networks = [
        'traefik-net'
        ],
    endpoint_spec = {
        'Ports': [
            {'Protocol': 'tcp', 'PublishedPort': 80, 'TargetPort': 80},
            {'Protocol': 'tcp', 'PublishedPort': 8080, 'TargetPort': 8080},
            {'Protocol': 'tcp', 'PublishedPort': 443, 'TargetPort': 443}
            ]
        },
    labels = {
        'traefik.enable': 'true',
        'traefik.port': '8080',
        'traefik.frontend.rule': 'Host:traefik.rowsheet.com'
        },
    constraints = [
        'node.role == manager'
        ]
        )
