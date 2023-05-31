import os
import sentry_sdk
import uuid
import requests
import json

from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer
from sentry_sdk.integrations.flask import FlaskIntegration

from handler import handle
from dotenv import load_dotenv

static_file_directory = os.environ.get("STATIC_DIRECTORY", "../webapp/out/")


if os.path.exists(".env") and os.path.getsize(".env") != 0:
    load_dotenv(verbose=True)
    print("✔  .env file loaded")
else:
    print("⚠  .env file not found, or is empty")

if os.environ.get("SENTRY_DSN") is not None:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENVIRONMENT"),
        integrations=[FlaskIntegration()],
    )
    print("✔  Sentry initialized")

if os.environ.get('TURNSTILE_SECRET_KEY') is not None:
    TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
    SITEVERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    print("✔  Turnstile initialized")
else:
    TURNSTILE_SECRET_KEY = "1x0000000000000000000000000000000AA"


def validate_turnstile(token, ip):
    # Prepare the data to send to the siteverify endpoint.
    data = {
        'secret': TURNSTILE_SECRET_KEY,
        'response': token,
        'remoteip': ip,
        'idempotency_key': str(uuid.uuid4())
    }

    # Make the POST request to the siteverify endpoint.
    result = requests.post(SITEVERIFY_URL, data=data)
    outcome = json.loads(result.text)

    return outcome


app = Flask(__name__, static_folder=static_file_directory, static_url_path="")


@app.before_request
def fix_transfer_encoding():
    """
    From of-watchdog python-flask template
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == "chunked":
        request.environ["wsgi.input_terminated"] = True


@app.route("/")
def index_route():
    return app.send_static_file("index.html")


@app.route('/validate', methods=['POST'])
def validate():
    # Extract the Turnstile response and remote IP from the request.
    token = request.form.get('cf-turnstile-response')
    ip = request.remote_addr

    outcome = validate_turnstile(token, ip)

    if outcome.get('success'):
        return "Validation successful", 200
    else:
        return "Validation failed: " + ', '.join(outcome.get('error-codes', [])), 400


@app.route("/kaaf", methods=["POST"])
def main_route():
    response, status = handle(request.json)
    return response, status


if __name__ == "__main__":
    http_server = WSGIServer(("", 5000), app)
    print("✔  Server started at http://localhost:5000/")
    http_server.serve_forever()
