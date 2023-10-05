from flask import request, jsonify
from . import api
from app.models import Pico

@api.route('/picos', methods=['POST'])
def post_pico():
    req = request.get_json()
    print(req)

    return jsonify({"status": "New Pico added"}), 201

@api.route('/picos', methods=['GET'])
def get_picos():
    picos = Pico.query.all()
    return jsonify([pico.to_dict() for pico in picos])
