from aft.db import get_db
from flask import Blueprint, make_response, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from aft.helpers import verify_token
from pprint import pprint

bp = Blueprint('auth', __name__, url_prefix='/auth')


def register_user(db_conn, user_details, user_type):
        # check if the user already exists
        cur = db_conn.cursor()
        check_query = "SELECT email, username from " + user_type + " WHERE "
        check_query += "email = '{}' OR username = '{}'".format(
        user_details["email"], user_details["username"])
        cur.execute(check_query)
        result = cur.fetchone()
        if not result:
            # proceed to insert details of the new user
            insert_query = ''
            if user_type == 'user':
                insert_query += "INSERT INTO user (email, username, city, region, phone, pwd) "
                insert_query += "VALUES ('{}', '{}', '{}', '{}', {}, '{}');".format(
                user_details["email"], user_details["username"], user_details["city"], user_details["region"],
                user_details["phone"], user_details["pwd"]
                )
            elif user_type == 'transporter':
                insert_query += "INSERT INTO transporter (email, username, dl_number, full_name, city, region, phone, pwd) "
                insert_query += "VALUES ('{}', '{}', '{}', '{}', {}, '{}')".format(
                user_details["email"], user_details["username"], user_details["dl_number"], 
                user_details["full_name"], user_details["city"], user_details["region"],
                user_details["phone"], user_details["pwd"]
                )
            cur.execute(insert_query)
            db_conn.commit()
            if cur.rowcount > 0:
                return {'success': 1, 'message': ('Registration '
                'successful')}, 200
            else:
                return {'success': 0, 'message': ('Server error while '
                'inserting data')}, 500
        elif user_details["email"] == result["email"]:
            return {'success': 0, 'message': 'Email already exists'}, 409
        elif user_details["username"] == result["username"]:
            return {'success': 0, 'message': 'Username already exists'}, 409

def fetch_user(db_conn, username, password, user_type):
    user = None
    with db_conn.cursor() as cur:
        if user_type is 'client':
            cur.execute("SELECT * FROM user WHERE username = '{}' AND pwd = '{}' LIMIT 1".format(username, password))
            db_conn.commit()
            user = cur.fetchone()

        elif user_type is 'transporter':
            cur.execute("SELECT * FROM transporter WHERE username = '{}' AND pwd = '{}' LIMIT 1".format(username, password))
            db_conn.commit()
            user = cur.fetchone()
    return user         

 
@bp.route('/register/<user_type>', methods=['POST'])
def do_registration(user_type):
    '''Get the users's information from POST data and inserts into the
    database'''
    db_conn = get_db()
    request_data = request.get_json(force=True)
    result, status = register_user(db_conn, request_data, user_type)
    return make_response(jsonify(result), status)


@bp.route('/login/client', methods=['POST'])
def do_client_login():
    '''This function checks POSTed data against what is in the database and
     returns a jwt to authorize users to use the site'''
    db = get_db()
    request_data = request.get_json(force=True)
    user_info = fetch_user(
        db, request_data['username'], request_data['pwd'], 'client'
        )

    if user_info is None:
        return make_response(
            jsonify({'success': 0, 'message': 'User not found'}), 404)

    elif user_info['pwd'] == request_data['pwd'] and user_info['username'] == request_data['username']:
        token = jwt.encode(
            {'typ': 'user',
             'sub': user_info['id'],
             'exp': datetime.utcnow() + timedelta(days=10)
             },
            current_app.config["SECRET_KEY"], algorithm='HS256').decode('utf-8')

        del user_info["pwd"]
        return make_response(jsonify({
                                    'success': 1,
                                    'message': 'Successful login',
                                    'user_details': user_info,
                                    'token': '{}'.format(token)
                                    }), 200)


@bp.route('/login/transporter', methods=['POST'])
def do_driver_login():
    db_conn = get_db()
    request_data = request.get_json(force=True)
    user_info = fetch_user(
        db_conn, request_data['username'], request_data['pwd'], 'transporter'
        )

    if not user_info:
        return make_response(
            jsonify({'success': 0, 'message': 'User not found'}), 404
            )
    elif user_info['pwd'] == request_data['pwd'] and user_info['username'] == request_data['username']:
        token = jwt.encode({
            'typ': 'transporter', 'sub': user_info['id'],
            'exp': datetime.now()+timedelta(
                days=10)}, current_app.config["SECRET_KEY"], algorithm='HS256').decode('utf-8')
        return jsonify({'success': 1, 'message': 'Successful login', 'token': '{}'.format(token)})       