from flask import Flask, jsonify, request, make_response
import pymysql.cursors
from datetime import datetime, timedelta
from jwt import encode, decode, get_unverified_header
import crypt

# create a secret for signing jwt's, this should later on be set in
# the environment variables for security purposes
secret = crypt.crypt('secreto', salt=crypt.METHOD_SHA256)

# connect to mysql db
connection = pymysql.connect(host='localhost',
                             user='ulembaya',
                             password='Mby4d3$$t',
                             db='askfortransport',
                             cursorclass=pymysql.cursors.DictCursor)

# obtain cursor to enable us to make db queries
cur = connection.cursor()
app = Flask(__name__)


@app.route('/auth/client', methods=['POST'])
def do_client_login():
        '''This function checks POSTed data against wht is in the database and returns a jwt to authorize users to use the site'''
        request_data = request.get_json(force=True)
        user_info = fetch_user(request_data['username'], request_data['pass'], 'client')

        if user_info is None:
                return jsonify({'message': 'User not found'})

        elif user_info['password'] == request_data['pass'] and user_info['username'] == request_data['username']:
                jwt = encode({'sub': user_info['id'], 'exp': datetime.now()+timedelta(
                        days=10)}, secret, algorithm='HS256')
                return jsonify({'message': 'Successful login', 'token': '{}'.format(jwt)})

        else:
                response = make_response(jsonify({'message': 'User not found'}), 404)
                return response


@app.route('/auth/driver', methods=['POST'])
def do_driver_login():
        request_data = request.get_json(force=True)
        user_info = fetch_user(request_data['username'], request_data['pass'], 'transporter')

        if user_info is None:
                return jsonify({'message': 'User not found'})

        elif user_info['password'] == request_data['pass'] and user_info['username'] == request_data['username']:
                jwt = encode({'sub': user_info['id'], 'exp': datetime.now()+timedelta(
                        days=10)}, secret, algorithm='HS256')
                return jsonify({'message': 'Successful login', 'token': '{}'.format(jwt)})

        else:
                response = make_response(jsonify({'message': 'User not found'}), 404)
                return response


def fetch_user(username, password, user_type):
        if user_type is 'client':
                cur.execute("SELECT * FROM user WHERE username = '{}' AND pwd = '{}' LIMIT 1".format(username, password))
        elif user_type is 'transporter':
                cur.execute("SELECT * FROM transporter WHERE username = '{}' AND pwd = '{}' LIMIT 1".format(username, password))

        return cur.fetchone()


def verify_token(token):
        ''' whenever a user sends a request accompanied by the jwt 
            we must check its validity'''
        payload = decode(token, secret, algorithm='HS256')
        if get_unverified_header(token)['alg'] is 'HS256':
                return True
        elif datetime.now().month - payload['exp'].month >= 1:
                return False
        else:
                return True