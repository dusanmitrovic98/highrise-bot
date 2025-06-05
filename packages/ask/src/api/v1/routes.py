from flask import Blueprint, jsonify

api_v1 = Blueprint('api_v1', __name__)

@api_v1.route('/status')
def status():
    return jsonify({'status': 'API v1 is working!'})
