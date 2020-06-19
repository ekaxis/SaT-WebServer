from flask import request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import *
from model import (app, db, agent_exists, Host)
from controller import Controller
from helper import keygen
import hashlib
import os.path
import threading

controller = Controller(db)
jsonify = Controller.jsonify # custom response json with headers

@app.route('/', methods=['GET', 'POST'])
def status_api():
    response = controller.guard()
    if not response.get('status'):
        return jsonify({'msg': ERROR[response.get('code')], 'ip': request.remote_addr}, 401)
    return jsonify({'version': '1.0.0'}, 200)

@app.route('/get/<string:hostname>')
def info_agent(hostname):
    data_json = request.get_json()
    if not isinstance(data_json, dict):
        return jsonify({'msg': ERROR[7]}, 400)

    key_master = data_json.get('apikey')
    if key_master is None:
        return jsonify({'msg': ERROR[6]}, 400)

    host = controller.host_by_hostname(hostname)
    if host is None:
        return jsonify({'msg': ERROR[8]}, 200)

    host_info = {
        'hostname': host.hostname, 'apikey': host.apikey, 'ip': host.ip
    }
    return jsonify({'host': host_info}, 200)

@app.route('/new', methods=['POST'])
def add_agent():
    data_json = request.get_json()
    if not isinstance(data_json, dict):
        return jsonify({'msg': ERROR[7]}, 400)

    key_master = data_json.get('apikey')
    ip_client = data_json.get('ip')
    hostname = data_json.get('hostname')

    if (hostname is None) or (ip_client is None) or (key_master is None):
        return jsonify({'msg': ERROR[6]}, 400)

    if key_master != KEY_MASTER:
        return jsonify({'msg': ERROR[2]}, 400)

    _ERROR = {
        1: 'user already exists in the database',
        2: 'unknown error when registering in the database'
    }
    
    api_key = keygen()
    response = controller.new_agent(hostname, api_key, ip_client)
    if response.get('code') == 0:
        return jsonify({'msg': 'user successfully registered', 'apikey': api_key})

    return jsonify({'msg': _ERROR.get(response.get('code'))}, 409)

@app.route('/upload', methods=['POST'])
def uploaded_file():
    ip = request.remote_addr
    response = controller.guard()
    if not response.get('status'):
        return jsonify({'msg': ERROR[response.get('code')]}, 401)

    if 'log' not in request.files:
        return jsonify({'msg': ERROR.get(4)}, 400)

    file = request.files['log']
    path_absolute = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.isfile(path_absolute):
        return jsonify({'msg': ERROR.get(5)}, 409)

    file.save(path_absolute)
    threading.Thread(target=controller.save, args=(path_absolute, ip, conn)).start()

    return jsonify({'msg': 'sent with success'}, 200)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
