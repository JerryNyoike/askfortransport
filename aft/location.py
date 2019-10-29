from flask import Blueprint, jsonify, make_response, current_app, request
from aft.db import get_db

bp = Blueprint('location', __name__, url_prefix='/location')


@bp.route("/cities", methods=['POST'])
def get_cities():
	cur = get_db().cursor()

	fetch_query = "SELECT * FROM city"
	cur.execute(fetch_query)

	cities = cur.fetchall()

	if not cities:
		response = {"success": 0, "message": "No cities found"}
		return make_response(jsonify(response), 404)
	else:
		response = {"success": 1, "message": "Cities found", "cities": cities}
		return make_response(jsonify(response), 200)
		
@bp.route("/regions/<city_id>", methods=['POST'])
def get_regions(city_id):
	cur = get_db().cursor()

	fetch_query = "SELECT * FROM regions WHERE city_id = %s" % city_id 
	cur.execute(fetch_query)

	regions = cur.fetchall()

	if not regions:
		response = {"success": 0, "message": "No regions found"}
		return make_response(jsonify(response), 404)
	else:
		response = {"success": 1, "message": "Regions found", "regions": regions}
		return make_response(jsonify(response), 200)
