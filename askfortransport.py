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

@app.route('/auth/register/<user_type>', methods=['POST'])
def do_registration(user_type):
        '''Get the users's information from POST data and inserts into the database'''
        request_data = request.get_json(force=True)
        result, status = register_user(request_data, user_type)
        return make_response(jsonify(result), status)
                

@app.route('/auth/login/client', methods=['POST'])
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

@app.route('/auth/login/driver', methods=['POST'])
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

@app.route("/vehicles", methods=['POST'])
@app.route("/vehicles/<search_params>", methods=['POST'])
def get_vehicles(search_params=None):
        fetch_query = "SELECT * FROM vehicle"
        #get any search parameters if any from the url
        #and include them in the SQL search query
        if search_params is not None:
                fetch_query += " WHERE "
                params = search_params.split("&")
                for i, param in enumerate(params):
                        key_value = param.split("=")
                        if i is not len(params) - 1:
                                fetch_query += key_value[0] + "=" + key_value[1] + " AND "
                        else:
                                fetch_query += key_value[0] + "=" + key_value[1]
        cur.execute(fetch_query) 
        result = cur.fetchall()
        if not result:
                return make_response(jsonify({'success': 0, 'message': 'No vehicles found'}), 404)
        else:
                return make_response(jsonify({'success': 1, 'vehicles': result}), 200)

def register_user(user_details, user_type):                
        #check if the user already exists
        check_query = "SELECT email, username from " + user_type + " WHERE "
        check_query += "email = '{}' OR username = '{}'".format(user_details["email"], user_details["username"])
        cur.execute(check_query)
        result = cur.fetchone()
        if not result:
                #proceed to insert details of the new user
                insert_query = ''
                if user_type == 'user':
                        insert_query += "INSERT INTO user (email, username, phone, pwd) "
                        insert_query += "VALUES ('{}', '{}', {}, '{}')".format(user_details["email"], 
                        user_details["username"], user_details["phone"], user_details["pwd"])
                elif user_type == 'transporter':
                        insert_query += "INSERT INTO transporter (email, username, dl_number, fullname, phone, pwd) "
                        insert_query += "VALUES ('{}', '{}', '{}', '{}', {}, '{}')".format(user_details["email"], 
                        user_details["username"], user_details["dl_number"], user_details["fullname"], 
                        user_details["phone"], user_details["pwd"])
                cur.execute(insert_query) 
                connection.commit()
                return {'success': 1, 'message': 'Registration succesful'}, 200
        elif user_details["email"] == result["email"]:
                return {'success': 0, 'message': 'Email already exists'}, 409
        elif user_details["username"] == result["username"]:
                return {'success': 0, 'message': 'Username already exists'}, 409
        
        
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