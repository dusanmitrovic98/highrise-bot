
from flask import Blueprint, jsonify

api_v2 = Blueprint('api_v2', __name__)

@api_v2.route('/status')
def status():
    return jsonify({'status': 'API v2 is working!'})
