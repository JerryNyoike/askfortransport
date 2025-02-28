import os
import pymysql.cursors
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from . import db, auth, vehicle, transporter, payments, location


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='$5$3Y/MPbv8Qi2nDv5M$z9rn56J9EDnw.bOtCpJSelh76uzkUsUHaDnHZ73D9g.',
        IMAGE_STORE_PATH='./static',
        DB_HOST='localhost',
        DB_USER='root',
        DB_PASS='',
        DB='askfortransport',
        CURSOR=pymysql.cursors.DictCursor
    )
    CORS(app)
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except (OSError):
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(vehicle.bp)
    app.register_blueprint(transporter.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(location.bp)

    return app
