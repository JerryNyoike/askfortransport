from datetime import datetime
import requests
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
        vehicle = request_data['vehicle_id']
        amount = request_data['amount']
        client = payload['sub']
        db_conn = get_db()
        cur = db_conn.cursor()
        client_phone_query = "SELECT phone FROM user WHERE id = {} LIMIT 1".format(client_id)
        cur.execute(client_phone_query)
        client_phone = cur.fetchone() 
        payment_response = make_payment(vehicle, amount, client_phone)
        if not payment_response: 
           return payment_response 
        else:
            return make_response({'status': 0, 'message': 'Unable to process payment.'})

        return make_response({'status': 1, 'message': 'success', 'data': userpayments})


@bp.route('/lnm_hook/<v_id>', methods=['POST'])
def lnm_webhook(v_id):
    payment_data = request.get_json()
    if not payment_data['Body']['stkCallback']['ResultCode']:
        # save payment details in the database
        db_conn = get_db()
        cur = db_conn.cursor()

        pay_id = uuid4()
        amount = payment_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
        receipt_no = payment_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]
        payment_time = payment_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"]
        client_no = payment_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]

        client_query = "SELECT id FROM user WHERE phone = {} LIMIT 1".format(client_no)
        cur.execute(client_query)
        client_id = cur.fetchone()

        payment_query = "INSERT INTO payment (payment_id, amount, receipt_id, client_id, vehicle_id, payment_time) VALUES '{}', {}, '{}', {}{}, {}".format(pay_id, amount, receipt_no, client_id, v_id, payment_time)
    
    return redirect(url_for('failed_payment')


def disburse_payment(transporter_no):
    if transporter_no is not None:
        api_token = current_app.config["TKN"]
        api_url = current_app.config["B2C_URL"]
        headers = {"Authorization": "Bearer {}".format(api_token)}
        payload = {
            "InitiatorName": "",
            "SecurityCredential": "",
            "CommandID": "",
            "Amount": "",
            "PartyA": "",
            "PartyB": "",
            "Remarks": "",
            "QueueTimeoutURL": "",
            "ResultURL": "",
            "Occassion": ""
            }

        response = requests.post(api_url, json=payload, headers = header)
        if response['ResponseCode'] == 0:
            return {"status": 0, "message": response['ResponseDescription']}

        return {"status": 1, "message": response['ResponseDescription']}

    return {"status": 1, "message": "Transporter's number cannot be blank."}

def make_payment(transporter, amount, client):
    access_token = current_app.config["TKN"]
    api_url = current_app.config["LNM_URL"]
    header = "Authorization: Bearer {}".format(access_token)
    pwd = b64encode((current_app.config["PASSKEY"]+current_app.config["SHORT_CODE"] + datetime.now().strftime("%Y%m%d%H%M%S")).encode("utf-8")).decode("utf-8")
    payload = {
            "BusinessShortCode": current_app.config["SHORT_CODE"],
            "Password": pwd,
            "Timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
            "TransactionType": "CustomerPaybillOnline",
            "Amount": amount,
            "PartyA": client,
            "PartyB": "174379",
            "PhoneNumber": client,
            "CallBackURL": ("http://ngrok.io/" + vehicle_id),
            "AccountReference": current_app.config["ACC_REF"],
            "TransactionDesc": " Transportation payment."
            }
    
    response = requests.post(api_url, json = payload, headers = header)
    if not response['ResponseCode']:
        return {"status": 1, "message": response["CustomerMessage"]
    
    return None
