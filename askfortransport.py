from flask import Flask, jsonify, request, make_response
from werkzeug.utils import secure_filename
import pymysql.cursors
from datetime import datetime, timedelta
import jwt
import os

# create a secret for signing jwt's, this should later on be set in
# the environment variables for security purposes
secret = "$5$3Y/MPbv8Qi2nDv5M$z9rn56J9EDnw.bOtCpJSelh76uzkUsUHaDnHZ73D9g."
ALLOWED_EXTENSIONS = ['jpeg', 'png', 'jpg']

# connect to mysql dbm
connection = pymysql.connect(host='localhost',
                             user='ulembaya',
                             password='Mby4d3$$t',
                             db='askfortransport',
                             cursorclass=pymysql.cursors.DictCursor)

# obtain cursor to enable us to make db queries

app = Flask(__name__)
app.config.from_mapping(
        IMAGE_STORE_PATH='/home/nyoike/Documents/images/'
)


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


def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decoded_token(tkn):
        if verify_token(tkn):
                return jwt.decode(tkn)
        else:
                return None


def verify_token(token):
        ''' whenever a user sends a request accompanied by the jwt
            this function checks its validity by looking at the algorithm used and the expiry time of the token'''
        try:
                jwt.decode(token, secret, algorithms=['HS256'])
                return True
        except jwt.ExpiredSignatureError:
                return False
        except jwt.InvalidAlgorithmError:
                return False

@app.route('/auth/client', methods=['POST'])
def do_client_login():
        '''This function checks POSTed data against wht is in the database and returns a jwt to authorize users to use the site'''
        request_data = request.get_json(force=True)
        user_info = fetch_user(request_data['username'], request_data['pass'], 'client')

        if user_info is None:
                return jsonify({'message': 'User not found'})

        elif user_info['pwd'] == request_data['pass'] and user_info['username'] == request_data['username']:
                token = jwt.encode({'sub': user_info['id'], 'exp': datetime.utcnow()+timedelta(
                        days=10)}, secret, algorithm='HS256').decode('utf-8')
                return jsonify({'message': 'Successful login', 'token': '{}'.format(token)})

        else:
                response = make_response(jsonify({'message': 'User not found'}), 404)
                return response


@app.route('/auth/driver', methods=['POST'])
def do_driver_login():
        request_data = request.get_json(force=True)
        user_info = fetch_user(request_data['username'], request_data['pass'], 'transporter')

        if user_info is None:
                return jsonify({'message': 'User not found'})

        elif user_info['pwd'] == request_data['pass'] and user_info['username'] == request_data['username']:
                token = jwt.encode({'sub': user_info['id'], 'exp': datetime.now()+timedelta(
                        days=10)}, secret, algorithm='HS256').decode('utf-8')
                return jsonify({'message': 'Successful login', 'token': '{}'.format(token)})

        else:
                response = make_response(jsonify({'message': 'User not found'}), 404)
                return response



@app.route('/images/vehicle/upload<vehicle_id>', methods=['POST'])
def upload_image(vehicle_id):
        #get token and check token validity
        token = request.headers['Authorization'].split(" ")[1]
        if vehicle_id is None:
                response = make_response(jsonify({"message": "You must specify the vehicle id to post a  picture of it."}), 400)
                return response
        
        elif verify_token(token) is True:
                if not request.files:
                        response = make_response(jsonify({"message": "no files uploaded"}), 400)
                        return response
                
                img = request.files['file']
                if img.filename == '':
                        response = make_response(jsonify({"message": "no uploaded"}), 400)
                        return response

                elif img and allowed_file(img.filename):
                        driver_id = jwt.decode(token, secret, algorithms=['HS256'])['sub']
                        filename = secure_filename(img.filename)
                        path = os.path.join(app.config['IMAGE_STORE_PATH'], str(driver_id), str(vehicle_id), filename)
                        if not os.path.exists(os.path.dirname(path)):
                                os.makedirs(os.path.dirname(path))

                        img.save(path)
                        # save the file path to the database
                        with connection.cursor() as cur:
                                cur.execute("UPDATE vehicle SET pictures = %s WHERE transporter_id = %s", (path, driver_id))
                                connection.commit()
                        
                        return jsonify({"message":"Successfully uploaded image"})
                        
                response = make_response(jsonify({"message":"Bad request"}, 400))
                return response