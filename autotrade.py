from flask import Flask, request, jsonify
from flask_cors import CORS
from members import members
from sendtrade import sendtrade
from memberspyramiding import memberspyramiding
from sendtradepyramiding import sendtradepyramiding
from pyramidingconversion import pyramidingconversion
import requests
import json
import psycopg2
import time
from pyupbit import Upbit
import pyupbit
from update import update
from pyramiding import pyramiding

def autotrade():


    mode = "deploy"

    DB_NAME = "pentaplant"
    DB_USER = "pentaplant"
    DB_PASS = "pentaplant_landingpage"
    DB_HOST = "localhost"
    DB_PORT = "5432" 
    dbconn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
    dbcur = dbconn.cursor()

    membersobj = members(dbcur, dbconn)

    sendtradeobj = sendtrade(dbcur, dbconn)

    memberspyramidingobj = memberspyramiding(dbcur,dbconn)

    sendtradepyramidingobj = sendtradepyramiding(dbcur,dbconn)

    pyramidingconversionobj = pyramidingconversion(dbcur,dbconn)

    updateobj = update(dbcur, dbconn)
    pyramidingobj = pyramiding(dbcur, dbconn)

    while(True):

        # fetches real time bitcoin price from the database
        #dbcur.execute("SELECT currentprice FROM realtime WHERE coin = %s", ("bitcoin",))
        #currentprice = dbcur.fetchall()[0][0]
        dbcur.execute("SELECT orderbook FROM realtime WHERE (coin, exchange) = (%s, %s)", ("BTC/USDT", "Upbit"))
        orderbook = dbcur.fetchall()[0][0]

        buyprice = orderbook["askprice"]
        sellprice = orderbook["bidprice"]

        # pyramiding.py, update.py, sendtrade.py
        # realtime_upbit.py, realtime_upbit_balance.py, upbitapi.py 
        
        result = pyramidingobj.updates(buyprice, sellprice)
        print(" ==== 11 ")


        result = sendtradeobj.buytrade(buyprice, sellprice, mode=mode)
  


        result = sendtradeobj.selltrade(buyprice, sellprice, mode=mode)


        """

        result = sendtradepyramidingobj.buytrade(buyprice, sellprice, mode=mode)
        print(" ==== 44 ")

        result = sendtradepyramidingobj.selltrade(buyprice, sellprice, mode=mode)
        print(" ==== 55")

        result = pyramidingobj.updates(buyprice, sellprice)
        print( " ==== 66")
        """






        """
        # checks whether the current price converts pyramiding or not
        result = pyramidingconversionobj.update(buyprice, sellprice)
        print( "  result    ", result)

        # updates the target prices if necessary
        result = membersobj.update(buyprice, sellprice)
        print(" result   ", result)
        #updates the pyramiding if necessary
        result = memberspyramidingobj.update(buyprice, sellprice)
        print(" result   ", result)
        


        # checks whether any one of them is enter and executes order
        result2 = sendtradeobj.buytrade(buyprice, sellprice, mode=mode)
        print(" result2  ", result2)
        # checks whether any one of them is sellable and executes order
        result3 = sendtradeobj.selltrade(buyprice, sellprice, mode=mode)
        print(" result3  ", result3)


        # checks whether any one of pyramiding is enter and executes order
        result4 = sendtradepyramidingobj.buytrade(buyprice, sellprice, mode=mode)
        print(" result4 ", result4)
        
        # cheecks whether any one of pyramiding is sellable and executes order
        result5 = sendtradepyramidingobj.selltrade(buyprice, sellprice, mode=mode)
        print(" result5 ", result5)

        

        # updates the target prices if necessary
        result6 = membersobj.update(buyprice, sellprice)
        print(" result6   ", result6)
        #updates the pyramiding if necessary
        result7 = memberspyramidingobj.update(buyprice, sellprice)
        print(" result   ", result7)
        """


        
        time.sleep(10)

        if mode != "deploy":
            break





if __name__ == "__main__":
    autotrade()


