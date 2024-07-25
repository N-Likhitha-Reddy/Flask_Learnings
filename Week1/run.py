from flask import Flask, request, jsonify
import json

flask_app = Flask(__name__)


@flask_app.route('/')
def index():
    return 'Server is running'


@flask_app.route('/post', methods=['POST'])
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
    return "data added successfully"


@flask_app.route('/get', methods=['GET'])
def get_data():
    try:
        with open("data_file.json", 'r') as r:
            content = r.read()
    except FileNotFoundError as ex:
        flask_app.logger.error("FileNotFoundError: data_file.json file not found")
        return "No data present in the file"
    if content:
        data = json.loads(content)
        flask_app.logger.info("Data successfully received")
        return data
    else:
        return "no data present in the file"


if __name__ == '__main__':
    flask_app.run(debug=True)