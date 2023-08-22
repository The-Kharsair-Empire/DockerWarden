import os

from dotenv import load_dotenv

import warnings
warnings.filterwarnings('ignore', message=".*OpenSSL")  # docker connection will give openssl warning as transport is
# not encrypted.

from flask import Flask
import uuid

load_dotenv()

from .server import server
from .api import api
from .authentication import login_manager

debug = True if os.getenv('DEBUG', 'FALSE') == 'TRUE' else False
if debug:
    run_config = {
        'ssl_context': (os.getenv('SSL_CERT', 'ssl/cert.pem'), os.getenv('SSL_KEY', 'ssl/key.pem')),
        'host': os.getenv('HOST_IP', '127.0.0.1'),
        'port': int(os.getenv('HOST_PORT', 8080))
    }
else:
    run_config = {
        'host': os.getenv('HOST_IP', '127.0.0.1'),
        'port': int(os.getenv('HOST_PORT', 8080))
    }


def init_flask():
    _app = Flask(__name__)
    with open('.env', 'r') as env:
        lines = env.readlines()
        for line in lines:
            k, v = line.split('=')
            _app.config[k] = v

    _app.register_blueprint(api)
    _app.register_blueprint(server)

    login_manager.init_app(_app)
    login_manager.login_view = 'server.login'

    _app.config['SECRET_KEY'] = uuid.uuid4().hex
    return _app
