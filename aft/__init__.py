import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='$5$3Y/MPbv8Qi2nDv5M$z9rn56J9EDnw.bOtCpJSelh76uzkUsUHaDnHZ73D9g.',
        IMAGE_STORE_PATH='static',
        DATABASE=connection
    )
    CORS(app)
    if test_config is None:
        app.config.from_mapping('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.make_dirs(app.instance_path)
    except (OSError):
        pass

    return app