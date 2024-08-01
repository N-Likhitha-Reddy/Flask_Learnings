import json

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from api.auth_apis import api_blueprint as auth_blueprint
from api.basic_get_and_post_apis import basic_api_blueprint as basic_get_post_blueprint

load_dotenv()


flask_app = Flask(__name__)
flask_app.secret_key = b'secret-key'


flask_app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(flask_app)


CORS(flask_app)
csrf = CSRFProtect(flask_app)


flask_app.register_blueprint(basic_get_post_blueprint, url_prefix='/api')
flask_app.register_blueprint(auth_blueprint, url_prefix='/auth')


class FileProcessingError(Exception):
    pass


@flask_app.errorhandler(FileProcessingError)
def handle_file_processing_error(error):
    response = jsonify({"message": str(error)})
    response.status_code = 500
    return response


@flask_app.route('/')
def index():
    return "WELCOME TO FLASK APP"


if __name__ == '__main__':
    try:
        with open('otp_data.json', 'r') as file:
            pass
    except FileNotFoundError:
        with open('otp_data.json', 'w') as file:
            json.dump({}, file)
    flask_app.run(debug=True)
