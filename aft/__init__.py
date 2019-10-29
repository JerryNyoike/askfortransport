import os
import pymysql.cursors
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from . import db, auth, vehicle, transporter, payments


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='$5$3Y/MPbv8Qi2nDv5M$z9rn56J9EDnw.bOtCpJSelh76uzkUsUHaDnHZ73D9g.',
        IMAGE_STORE_PATH='static',
        DB_HOST='localhost',
        DB_USER='root',
        DB_PASS='rootlikesmysql-db',
        DB='askfortransport',
        CURSOR=pymysql.cursors.DictCursor,
        CONSUMER_KEY = "35knXduhzqI4XdQFWMvdnDi6dTVQ9ret",
        CONSUMER_SECRET = "ZBAMy6p24luLJPSG",
        PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
        ACC_REF = "AskForTransport",
        TKN = "GeTSMlyyykeFs27OTV7wDtbGBB1Q",
        LNM_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        B2C_URL = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest",
        CALLBACK_URL = "http://0dfe3bc0.ngrok.io/payment/lnmhook/{}/{}",
        RESULT_URL = "/payment/disbursement/hook/<v_id>/<transporter_id>",
        QUEUETIMEOUT_URL = "/payment/queuetimeout",
        SHORT_CODE = "600284",
        LNM_SHORT_CODE = "174379"
    )
    CORS(app)

    try:
        os.makedirs(app.instance_path)
    except (OSError):
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(vehicle.bp)
    app.register_blueprint(transporter.bp)
    app.register_blueprint(payments.bp)

    return app
