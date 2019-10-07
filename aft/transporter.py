from flask import Blueprint, jsonify, make_response, current_app, request
from aft.helpers import verify_token
from aft.db import get_db

bp = Blueprint('transporter', __name__, url_prefix='/transporter')

@bp.route("/profile", methods=['POST'])
def get_driver_profile():
    cur = get_db().cursor()
    token =  verify_token(request.headers['Authorization'].split(" ")[1], current_app.config['SECRET_KEY'])
    print(request.method)

    if not token:
            return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
    elif token["typ"] != "transporter":
            return make_response(jsonify({"success": 0, "message": "You need to be logged in as a driver to get profile"}), 400)

    cur.execute("SELECT * FROM transporter WHERE id = {}".format(token["sub"])) 
    response = {"success": 1, "details": cur.fetchone()}
    cur.execute("SELECT * FROM vehicle WHERE transporter_id = {}".format(token["sub"]))
    vehicles = cur.fetchall()
    response ["vehicles"] = vehicles
    if not vehicles:
            response["vehicles"] = "No vehicles found"
    return make_response(jsonify(response), 200)