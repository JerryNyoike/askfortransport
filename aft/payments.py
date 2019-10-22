from uuid import uuid4
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


@bp.route('/debit', methods=['POST'])
def debit():
    payload = verify_token(request.headers['Authorization'].split(' ')[1], current_app.config['SECRET_KEY'])
    if not payload:
        return make_response({'status': 0, 'message': 'Must be logged in to make a payment.'}, 404)
    else:
        request_data = get_json()
        transporter = request_data['transporter']
        amount = request_data['amount']
        client = payload['sub']
        db_conn = get_db()
        cur = db_conn.cursor()

        if make_payment(transporter, amount, client):
            # write payment information to the database
            pay_id = uuid4()

            query = "INSERT INTO payment (payment_id, credit, debit) VALUES {}, {}, {} WHERE trip.user_id = {}".format(pay_id, 0, amount, payload['sub'])
            cur.execute(query)
            user_payments = cur.fetchall()

        else:
            return make_response({'status': 0, 'message': 'Unable to process payment.'})

        return make_response({'status': 1, 'message': 'success', 'data': userpayments})
