from flask import Flask
from flask import request
from flask import Response
from rs_utils import logger
import json
import hmac
import hashlib

app = Flask(__name__)

GITHUB_SECRET="VC83D7PVEVHYMXMK8AR7KHIS6WBIFK6DNHUVWQB0276EPGA1E0OIVMX"

def parse_data(request_body):
    data = json.loads(request_body.decode('utf-8'))
    if "ref_type" not in data:
        return
    ref_type = data["ref_type"]
    if ref_type != "tag":
        return
    tag = data["ref"]
    repository = "github.com:%s.git" % data["repository"]["full_name"]
    logger.success("%s : %s" % (
        tag,
        repository,
    ))

def verify_hash(request_body, x_hub_signature):
    h = hmac.new(
        bytes(GITHUB_SECRET,encoding='utf8'),
        request_body,
        hashlib.sha1
    )
    return hmac.compare_digest(
        bytes("sha1=" + h.hexdigest(),encoding='utf8'),
        bytes(x_hub_signature,encoding='utf8')
    )

@app.route('/D7XE1L70QSTOUAFW5F3TYC29GUG2H9AJ3A3MMC7U87KMI6NRPEZX0WJ',methods=['POST','GET'])
def index():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    request_body = request.get_data()

    if verify_hash(request_body, x_hub_signature):
        logger.success('Success!')
        x_github_event = request.headers.get('X-GitHub-Event')
        logger.debug(x_github_event, line=True)
        parse_data(request_body)
        return Response("Thanks", 200)
    else:
        logger.error('No match!')
        return Response("502 Bad Gateway", 502)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000
    )
