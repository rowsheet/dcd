import docker

client = docker.from_env()

# Create the apache service.
client.services.create(
    image = 'httpd:alpine',
    networks = [
        'traefik-net'
        ],
    labels = {
        'traefik.enable': 'true',
        'traefik.port': '80',
        'traefik.frontend.rule': 'Host:apache.rowsheet.com'
        },
    name = 'apache'
        )
