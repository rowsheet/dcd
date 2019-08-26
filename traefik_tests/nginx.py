import docker

client = docker.from_env()

# Create the nginx service.
client.services.create(
    image = 'nginx:alpine',
    networks = [
        'traefik-net'
        ],
    labels = {
        'traefik.enable': 'true',
        'traefik.port': '80',
        'traefik.frontend.rule': 'Host:nginx.rowsheet.com'
        },
    name = 'nginx'
        )
