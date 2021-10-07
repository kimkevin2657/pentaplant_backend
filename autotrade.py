from flask import Flask, request, jsonify
from flask_cors import CORS
from members import members
from sendtrade import sendtrade
import requests
import json
import psycopg2
import time


def autotrade():
    DB_NAME = "pentaplant"
    DB_USER = "pentaplant"
    DB_PASS = "pentaplant_landingpage"
    DB_HOST = "localhost"
    DB_PORT = "5432" 
    dbconn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
    dbcur = dbconn.cursor()

    membersobj = members(dbcur, dbconn)

    sendtradeobj = sendtrade(dbcur, dbconn)

    while(True):

        # fetches real time bitcoin price from the database
        #dbcur.execute("SELECT currentprice FROM realtime WHERE coin = %s", ("bitcoin",))
        #currentprice = dbcur.fetchall()[0][0]
        dbcur.execute("SELECT orderbook FROM realtime WHERE (coin, exchange) = (%s, %s)", ("BTC/USDT", "Upbit"))
        orderbook = dbcur.fetchall()[0][0]

        buyprice = orderbook["askprice"]
        sellprice = orderbook["bidprice"]

        # updates the target prices if necessary
        result = membersobj.update(buyprice, sellprice)
        print(" result   ", result)

        # checks whether any one of them is enter and executes order
        result2 = sendtradeobj.buytrade(buyprice, sellprice)
        print(" result2  ", result2)

        # checks whether any one of them is sellable and executes order
        result3 = sendtradeobj.selltrade(buyprice, sellprice)
        print(" result3  ", result3)

        # updates the target prices if necessary
        result4 = membersobj.update(buyprice, sellprice)
        print(" result4   ", result4)

        time.sleep(5)

        break



if __name__ == "__main__":
    autotrade()


