from flask import Blueprint, jsonify, request, session, current_app as flask_app
import json

basic_api_blueprint = Blueprint('basic_api_blueprint', __name__)


@basic_api_blueprint.route('/')
def index():
    flask_app.logger.info("Checking the count of webpage accessing")
    if 'count' in session:
        session['count'] += 1
    else:
        session['count'] = 1
    return f"Number of times page opened is: {session['count']}"


@basic_api_blueprint.route('/post', methods=['POST'])
def post_data():
    try:
        with open("data_file.json", 'r') as r:
            content = r.read()
    except FileNotFoundError as ex:
        return "Mentioned file doesn't exist"
    if not content:
        data = dict()
        data['Likhitha'] = 'Python'
        with open("data_file.json", 'w') as w:
            w.write(json.dumps(data))
    else:
        with open("data_file.json", 'r') as r:
            data = json.loads(r.read())
            data['Likhitha'] = 'Python'
        with open("data_file.json", 'w') as w:
            w.write(json.dumps(data))
    return "Data added successfully"


@basic_api_blueprint.route('/get', methods=['GET'])
def get_data():
    try:
        with open("data_file.json", 'r') as r:
            content = r.read()
    except FileNotFoundError as ex:
        return "No data present in the file"
    if content:
        data = json.loads(content)
        flask_app.logger.info("Data successfully received")
        return data
    else:
        return "No data present in the file"
