from flask import Flask, request, logging, jsonify
from flask_cors import CORS, cross_origin
#from data import Articles
from passlib.hash import sha256_crypt
from functools import wraps
import json
from flask import jsonify
import flask_praetorian
import psycopg2

import base64

guard = flask_praetorian.Praetorian()
cors = CORS()

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["SECRET_KEY"] = "temp secret"
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

cors.init_app(app)





DB_NAME = "pentaplant"
DB_USER = "pentaplant"
DB_PASS = "pentaplant_landingpage"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()







@app.route('/login', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def login():
    if request.method == "POST":
        return json.dumps({"success": True}), 200, {"contentType": "application/json"}


@app.route("/transactionhistory", methods=["GET", "POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def transactionhistory():
    if request.method == "POST":
        userid = 1

        cur.execute("SELECT id, entrytime, currency, amount, baseamount, entryprice, side FROM transaction WHERE userid = %s", (userid,))

        temp = cur.fetchall()
        print(temp)
        if len(temp) != 0:
            temp = sorted(temp)
            templist = []
            for i in range(0, len(temp)):
                temptemp = {
                    "no": i+1,
                    "date": temp[i][1][:10],
                    "coin": temp[i][2],
                    "type": temp[i][6],
                    "amount": "{:.4f}".format(temp[i][3]),
                    "price": "{:.2f}".format(temp[i][5]),
                    "worth": "{:.0f}".format(temp[i][4])
                }
                templist.append(temptemp)
            

            return json.dumps({"data": templist}), 200, {"ContentType": "application/json"}
        else:
            templist = []
            temptemp = {
					"no": 2,
					"date": '2021-05-03',
					"time": '14:00',
					"coin": 'BTC',
					"type": 'BTC',
					"amount": '200',
					"price": '400$',
					"worth": 'N/A'
			}
            templist.append(temptemp)

            return json.dumps({"data": templist}), 200, {"ContentType": "application/json"}



@app.route('/healthcheck', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def healthcheck():
    if request.method == "GET":
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


if __name__ == '__main__':
#    app.config['SECRET_KEY'] = 'Gmc@1234!'
#    csrf = CSRFprotect()
#    csrf.init_app(app)
    app.secret_key='secret123'
#    app.run(host='0.0.0.0', port=80, debug=True)
    app.run(host='0.0.0.0', port=5055, debug=True)







