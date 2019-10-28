from flask import Blueprint, jsonify, make_response, current_app, request
from aft.helpers import verify_token
from aft.db import get_db
from aft.helpers import verify_token

bp = Blueprint('vehicle', __name__, url_prefix='/vehicle')


@bp.route("/", methods=['POST'])
@bp.route("/<search_params>", methods=['POST'])
def get_vehicles(search_params=None):
    cur = get_db().cursor()

    fetch_query = "SELECT vehicle.id, vehicle.vehicle_type, vehicle.capacity, vehicle.price, vehicle.number_plate, vehicle.pictures, vehicle.booked, transporter.email, transporter.full_name, transporter.phone FROM vehicle INNER JOIN transporter ON vehicle.transporter_id=transporter.id"
    #get any search parameters if any from the url
    #and include them in the SQL search query
    if search_params is not None:
            fetch_query += " WHERE "
            params = search_params.split("&")
            for i, param in enumerate(params):
                    key_value = param.split("=")
                    if key_value[0] is not None and key_value[1] is not None:
                        if i is not len(params) - 1:
                            if key_value[0] == "min_price":
                                fetch_query += "price > " + key_value[1] + " AND "
                            elif key_value[0] == "max_price":
                                fetch_query += "price < " + key_value[1] + " AND "
                            else:
                                fetch_query += key_value[0] + "='" + key_value[1] + "' AND "
                        else:
                            if key_value[0] == "min_price":
                                fetch_query += "price > " + key_value[1]
                            elif key_value[0] == "max_price":
                                fetch_query += "price < " + key_value[1]
                            else:
                                fetch_query += key_value[0] + "='" + key_value[1] + "'"

    cur.execute(fetch_query) 
    result = cur.fetchall()
    if not result:
        return make_response(jsonify({'success': 0, 'message': 'No vehicles found'}), 404)
    else:
        return make_response(jsonify({'success': 1, 'message': "Vehicles found", 'vehicles': result}), 200)

@bp.route("/register", methods=['POST'])
def register_vehicle():
    db_conn = get_db()
    cur = db_conn.cursor()

    body = request.get_json(force=True)
    
    #get token and check token validity  
    token = verify_token(request.headers['Authorization'].split(" ")[1], current_app.config['SECRET_KEY'])

    if not token:
        return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
    if token["typ"] != "transporter":
        return make_response(jsonify({"success": 0, "message": "You need to be logged in as a driver to register a vehicle"}), 400)

    insert_query = "INSERT INTO vehicle (vehicle_type, capacity, price, number_plate, pictures, transporter_id, booked) VALUES "
    insert_query += "('{}', '{}', '{}', '{}', 'No image', {}, 'no')".format(body["type"], body["capacity"], body["price"], body["number_plate"], token["sub"])

    cur.execute(insert_query)
    db_conn.commit()
    if cur.rowcount > 0:     
        fetch_query = "SELECT id FROM vehicle WHERE number_plate = '%s'" % body["number_plate"]
        cur.execute(fetch_query)
        response = jsonify({"success": 1, "vehicle_id": cur.fetchone()["id"]})
        return make_response(response, 200)


@bp.route('/book/<v_id>', methods=['POST'])
def book_vehicle(v_id):
    db_conn = get_db()
    cur = db_conn.cursor()

    # get vehicle id from the route
    v_id = int(v_id)
    if v_id is None:
        return make_response(jsonify({"success": 0, "message": "Specify vehicle to book"}), 400)

    token = verify_token(request.headers['Authorization'].split(" ")[1], current_app.config['SECRET_KEY'])

    if not token:
        return make_response(jsonify({"success": 0, "message": "Client doesn't exist"}), 404)
    elif token['typ'] != 'user':
        return make_response(jsonify({"success": 0, "message": "You must have logged in with a client account to book a vehicle."}))

    # check that vehicle exists
    cur.execute("SELECT * FROM vehicle WHERE id = {}".format(v_id))
    db_conn.commit()

    vehicle = cur.fetchone()
    if vehicle['booked'] != 'no':
        return make_response(jsonify({"success": 0, "message": "The vehicle is not available for booking"}), 404)

    cur.execute("UPDATE vehicle SET booked = %s WHERE id = %s", (token['sub'], v_id))
    db_conn.commit()

    if cur.rowcount < 0:
        return make_response(jsonify({"success": 0, "message": "Booking Unsuccessful"}), 500)

    return make_response(jsonify({"success": 1, "message": "Successfully booked vehicle"}), 200)

@bp.route('/free/<v_id>', methods=['POST'])
def free_vehicle(v_id):
    db_conn = get_db()
    cur = db_conn.cursor()

    # get vehicle id from the route
    v_id = int(v_id)
    if v_id is None:
        return make_response(jsonify({"success": 0, "message": "Specify vehicle to free"}), 400)

    token = verify_token(request.headers['Authorization'].split(" ")[1], current_app.config['SECRET_KEY'])

    if not token:
        return make_response(jsonify({"success": 0, "message": "Driver doesn't exist"}), 404)
    elif token['typ'] != 'driver':
        return make_response(jsonify({"success": 0, "message": "You must have logged in with a driver account to free a vehicle."}))

    # check that vehicle exists
    cur.execute("SELECT * FROM vehicle WHERE id = {}".format(v_id))
    db_conn.commit()

    vehicle = cur.fetchone()
    if vehicle['booked'] == 'no':
        return make_response(jsonify({"success": 0, "message": "The vehicle is already available for booking"}), 404)

    cur.execute("UPDATE vehicle SET booked = %s WHERE id = %s", ('no', v_id))
    db_conn.commit()

    if cur.rowcount < 0:
        return make_response(jsonify({"success": 0, "message": "Freeing vehicle was unsuccessful"}), 500)

    return make_response(jsonify({"success": 1, "message": "Vehicle is now available for booking"}), 200)


@bp.route('/images/upload/<vehicle_id>', methods=['POST'])
def upload_image(vehicle_id):
    db_conn = get_db()
    cur = db_conn.cursor()

    #get token and check token validity     
    token = verify_token(request.headers['Authorization'].split(" ")[1], current_app.config['SECRET_KEY']) 

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
        path = os.path.join(current_app.config['IMAGE_STORE_PATH'], str(token["sub"]), body["filename"])
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        with open(path, "wb") as f:
            f.write(b64decode(body["image"]))
            f.close()

        # save the file path to the database
        cur.execute("UPDATE vehicle SET pictures = %s WHERE id = %s", (path, vehicle_id))
        db_conn.commit()
        return make_response(jsonify({"success": 1, "message":"Successfully uploaded image"}), 200)
