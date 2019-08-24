import docker

client = docker.from_env()

client.services.create(
    image = 'rowsheet/hello-flask:dev',
    networks = [
        'traefik-net'
        ],
    labels = {
        'traefik.enable': 'true',
        'traefik.port': '80',
        'traefik.frontend.rule': 'Host:dev.hello-flask-nginx.alpinecover.com'
        },
    name = 'dev--hello-flask-nginx',
    env = [
        "HELLO_FLASK_PORT=8000",
        "HELLO_FLASK_MESSAGE=Nginx hello-flask:dev.",
    ]
        )
