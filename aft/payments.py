import uuid
from flask import Blueprint, request, make_response, jsonify, current_app
from . import helpers
from aft.db import get_db


bp = Blueprint('payment', __name__, url_prefix='payment')

@bp.route('/get/all', methods=['POST'])
def get_user_payments(): 
    payload = verify_token(request.headers['Authorization'].split(' ')[1], current_app.config['SECRET_KEY'])
    if not payload:
        return make_response({'status': 0, 'message': 'Must be logged in to check payment history.'}, 404)
    else:
        db_conn = get_db()
        cur = db_conn.cursor()

        query = "SELECT * FROM payment LEFT JOIN ON payment.trip_id = trip.trip_id "
        query += "WHERE trip.user_id = {}".format(payload['sub'])
        cur.execute(query)
        user_payments = cur.fetchall()

        return make_response({'status': 1, 'message': 'success', 'data': userpayments})
