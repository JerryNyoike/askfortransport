import os
import pymysql.cursors
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from . import db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='$5$3Y/MPbv8Qi2nDv5M$z9rn56J9EDnw.bOtCpJSelh76uzkUsUHaDnHZ73D9g.',
        IMAGE_STORE_PATH='static',
        DB_HOST='localhost',
        DB_USER='root',
        DB_PASS='rootlikesmysql-db',
        DB='askfortransport',
        CURSOR=pymysql.cursors.DictCursor
    )
    CORS(app)
    if test_config is None:
        pass
        # app.config.from_mapping('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except (OSError):
        pass

    return app