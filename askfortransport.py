from flask import Flask, jsonify, request, make_response
from werkzeug.utils import secure_filename
import pymysql.cursors
from datetime import datetime, timedelta
import jwt
import os
from flask_cors import CORS
from base64 import b64decode

# create a secret for signing jwt's, this should later on be set in
# the environment variables for security purposes
secret = "$5$3Y/MPbv8Qi2nDv5M$z9rn56J9EDnw.bOtCpJSelh76uzkUsUHaDnHZ73D9g."
ALLOWED_EXTENSIONS = ['jpeg', 'png', 'jpg']

# connect to mysql dbm
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='askfortransport',
                             cursorclass=pymysql.cursors.DictCursor)

# obtain cursor to enable us to make db queries
cur = connection.cursor()

app = Flask(__name__)
app.config.from_mapping(
        IMAGE_STORE_PATH='static'
)

CORS(app)

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_token(token):
        ''' whenever a user sends a request accompanied by the jwt
            this function checks its validity by looking at the algorithm used and the expiry time of the token'''
        try:
                return jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
                return False
        except jwt.InvalidAlgorithmError:
                return False

def fetch_user(username, password, user_type):
        user = None
        with connection.cursor() as cur:
                if user_type is 'client':
                        cur.execute("SELECT * FROM user WHERE username = '{}' AND pwd = '{}' LIMIT 1".format(username, password))
                        connection.commit()
                        user = cur.fetchone()

                elif user_type is 'transporter':
                        cur.execute("SELECT * FROM transporter WHERE username = '{}' AND pwd = '{}' LIMIT 1".format(username, password))
                        connection.commit()
                        user = cur.fetchone()
        return user         

        
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
                        insert_query += "INSERT INTO transporter (email, username, dl_number, full_name, phone, pwd) "
                        insert_query += "VALUES ('{}', '{}', '{}', '{}', {}, '{}')".format(user_details["email"], 
                        user_details["username"], user_details["dl_number"], user_details["full_name"], 
                        user_details["phone"], user_details["pwd"])
                cur.execute(insert_query) 
                connection.commit()
                if cur.rowcount > 0:
                        return {'success': 1, 'message': 'Registration succesful'}, 200
                else:
                        return {'success': 0, 'message': 'Server error while inserting data'}, 500
        elif user_details["email"] == result["email"]:
                return {'success': 0, 'message': 'Email already exists'}, 409
        elif user_details["username"] == result["username"]:
                return {'success': 0, 'message': 'Username already exists'}, 409

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
                return make_response(jsonify({'success': 0, 'message': 'User not found'}), 404)
        elif user_info['pwd'] == request_data['pass'] and user_info['username'] == request_data['username']:
                token = jwt.encode({'typ': 'client', 'sub': user_info['id'], 'exp': datetime.utcnow()+timedelta(
                        days=10)}, secret, algorithm='HS256').decode('utf-8')
                return make_response(jsonify({'success': 1, 'message': 'Successful login', 'token': '{}'.format(token)}), 200)

@app.route('/auth/login/driver', methods=['POST'])
def do_driver_login():
        request_data = request.get_json(force=True)
        user_info = fetch_user(request_data['username'], request_data['pass'], 'transporter')

        if not user_info:
                return make_response(jsonify({'success': 0, 'message': 'User not found'}), 404)
        elif user_info['pwd'] == request_data['pass'] and user_info['username'] == request_data['username']:
                token = jwt.encode({'typ': 'driver', 'sub': user_info['id'], 'exp': datetime.now()+timedelta(
                        days=10)}, secret, algorithm='HS256').decode('utf-8')
                return jsonify({'success': 1, 'message': 'Successful login', 'token': '{}'.format(token)})

@app.route("/vehicles", methods=['POST'])
@app.route("/vehicles/<search_params>", methods=['POST'])
def get_vehicles(search_params=None):
        fetch_query = "SELECT vehicle.id, vehicle.vehicle_type, vehicle.capacity, vehicle.price, vehicle.number_plate, vehicle.pictures, vehicle.booked, transporter.email, transporter.full_name, transporter.phone FROM vehicle INNER JOIN transporter ON vehicle.transporter_id=transporter.id"
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
        print("\n\n" + fetch_query + "\n\n")
        cur.execute(fetch_query) 
        result = cur.fetchall()
        if not result:
                return make_response(jsonify({'success': 0, 'message': 'No vehicles found'}), 404)
        else:
                return make_response(jsonify({'success': 1, 'message': "Vehicles found", 'vehicles': result}), 200)

@app.route("/register_vehicle", methods=['POST'])
def register_vehicle():
        body = request.get_json(force=True)
        
        #get token and check token validity  
        token = verify_token(request.headers['Authorization'].split(" ")[1])

        if not token:
                return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
        if token["typ"] != "driver":
                return make_response(jsonify({"success": 0, "message": "You need to be logged in as a driver to register a vehicle"}), 400)

        insert_query = "INSERT INTO vehicle (vehicle_type, capacity, price, number_plate, pictures, transporter_id, booked) VALUES "
        insert_query += "('{}', '{}', '{}', '{}', 'No image', {}, 'no')".format(body["type"], body["capacity"], body["price"], body["number_plate"], token["sub"])
        cur.execute(insert_query)
        connection.commit()
        if cur.rowcount > 0:     
                fetch_query = "SELECT id FROM vehicle WHERE number_plate = '%s'" % body["number_plate"]
                cur.execute(fetch_query)
                response = jsonify({"success": 1, "vehicle_id": cur.fetchone()["id"]})
                return make_response(response, 200)

@app.route('/images/vehicle/upload/<vehicle_id>', methods=['POST'])
def upload_image(vehicle_id):
        #get token and check token validity     
        token = verify_token(request.headers['Authorization'].split(" ")[1]) 

        if vehicle_id is None:
                return make_response(jsonify({"success": 0, "message": "You must specify the vehicle id to post a  picture of it."}), 400)
        elif not token:
                return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
        elif token["typ"] != "driver":
                return make_response(jsonify({"success": 0, "message": "You need to be logged in as a driver to register a vehicle"}), 400)

        body = request.get_json(force=True)

        if body["image"] == '':
                return make_response(jsonify({"success": 0, "message": "no files uploaded"}), 400)
        elif body["image"] and allowed_file(body["filename"]):
                filename = secure_filename(body["filename"])
                path = os.path.join(app.config['IMAGE_STORE_PATH'], str(token["sub"]), body["filename"])
                if not os.path.exists(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))

                with open(path, "wb") as f:
                        f.write(b64decode(body["image"]))
                        f.close()

                # save the file path to the database
                cur.execute("UPDATE vehicle SET pictures = %s WHERE id = %s", (path, vehicle_id))
                connection.commit()
                return make_response(jsonify({"success": 1, "message":"Successfully uploaded image"}), 200)

@app.route("/driver_profile", methods=['POST'])
def get_driver_profile():
        token =  verify_token(request.headers['Authorization'].split(" ")[1])

        if not token:
                return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
        elif token["typ"] != "driver":
                return make_response(jsonify({"success": 0, "message": "You need to be logged in as a driver to get profile"}), 400)

        cur.execute("SELECT * FROM transporter WHERE id = {}".format(token["sub"])) 
        response = {"success": 1, "details": cur.fetchone()}
        cur.execute("SELECT * FROM vehicle WHERE transporter_id = {}".format(token["sub"]))
        vehicles = cur.fetchall()
        response ["vehicles"] = vehicles
        if not vehicles:
                response["vehicles"] = "No vehicles found"
        return make_response(jsonify(response), 200)

@app.route('/vehicle/book/<v_id>', methods=['POST'])
def book_vehicle(v_id):
        # get vehicle id from the route
        v_id = int(v_id)
        if v_id is None:
                return make_response(jsonify({"success": 0, "message": "Specify vehicle to book"}), 400)

        token = verify_token(request.headers['Authorization'].split(" ")[1])

        if not token:
                return make_response(jsonify({"success": 0, "message": "Client doesn't exist"}), 404)
        elif token['typ'] != 'client':
                return make_response(jsonify({"success": 0, "message": "You must have logged in with a client account to book a vehicle."}))

        # check that vehicle exists
        cur.execute("SELECT * FROM vehicle WHERE id = {}".format(v_id))
        connection.commit()

        vehicle = cur.fetchone()
        if vehicle['booked'] != 'no':
                return make_response(jsonify({"success": 0, "message": "The vehicle is not available for booking"}), 404)

        cur.execute("UPDATE vehicle SET booked = %s WHERE id = %s", (token['sub'], v_id))
        connection.commit()

        if cur.rowcount < 0:
                return make_response(jsonify({"success": 0, "message": "Booking Unsuccessful"}), 500)

        return make_response(jsonify({"success": 1, "message": "Successfully booked vehicle"}), 200)

@app.route('/vehicle/free/<v_id>', methods=['POST'])
def free_vehicle(v_id):
        # get vehicle id from the route
        v_id = int(v_id)
        if v_id is None:
                return make_response(jsonify({"success": 0, "message": "Specify vehicle to free"}), 400)

        token = verify_token(request.headers['Authorization'].split(" ")[1])

        if not token:
                return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
        elif token['typ'] != 'driver':
                return make_response(jsonify({"success": 0, "message": "You must have logged in with a driver account to free a vehicle."}))

        # check that vehicle exists
        cur.execute("SELECT * FROM vehicle WHERE id = {}".format(v_id))
        connection.commit()

        vehicle = cur.fetchone()
        if vehicle['booked'] == 'no':
                return make_response(jsonify({"success": 0, "message": "The vehicle is already available for booking"}), 404)

        cur.execute("UPDATE vehicle SET booked = %s WHERE id = %s", ('no', v_id))
        connection.commit()

        if cur.rowcount < 0:
                return make_response(jsonify({"success": 0, "message": "Freeing vehicle was unsuccessful"}), 500)

        return make_response(jsonify({"success": 1, "message": "Vehicle is now available for booking"}), 200)
