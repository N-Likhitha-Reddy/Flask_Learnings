import pytest
from flask import Flask
from flask.testing import FlaskClient
from api.auth_apis import api_blueprint as auth_blueprint
from api.basic_get_and_post_apis import basic_api_blueprint as basic_get_post_blueprint
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.secret_key = b'secret-key'
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

    app.register_blueprint(basic_get_post_blueprint, url_prefix='/api')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
