
import random
import numpy as np
import asyncio 
import time
import json
import requests
import psycopg2

from time import gmtime, strftime
import datetime
import pytz

from pyupbit import Upbit
import pyupbit

from upbitapi import upbitapi
from pyramiding import pyramiding

class sendtrade:
    def __init__(self, dbcur, dbconn):
        self.dbcur = dbcur
        self.dbconn = dbconn


    # finds the current time in Asia/Seoul in format YYYY-MM-DD hh:mm:ss
    def currenttime(self):
        tz1 = pytz.timezone("UTC")
        tz2 = pytz.timezone("Asia/Seoul")
        dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
        dt = tz1.localize(dt)
        dt = dt.astimezone(tz2)
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt


    def buytrade(self, buyprice, sellprice, mode="deploy"):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            userid = userlist[i][0]

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
            botsettings = self.dbcur.fetchall()[0]

            if botsettings[0]["active"] == False:
                continue

            apikeys = []
            upbit = []
            if mode == "deploy":
                apikeys = self.dbcur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userlist[i][0],))
                apikeys = self.dbcur.fetchall()[0]
                upbit = Upbit(apikeys[0], apikeys[1])

            maxrange = 0
            for q in range(0, len(botsettings)):
                if botsettings[q]["active"] == True:
                    maxrange
            maxrange += 1

            self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
            botinfo = self.dbcur.fetchall()[0]

            self.dbcur.execute("SELECT botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding FROM botsdata WHERE userid = %s", (userlist[i][0],))
            botinfopyramiding = self.dbcur.fetchall()[0]

            for j in range(0, maxrange):
                
                if botsettings[j]["currpyramiding"] == False:
                    print(" ============ currently pyramiding is false, so downpyramiding sendtrade buytrade logic sent")
                    currlist = botinfo[j]["data"]
                    currentered = False
                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == False:
                            if float(currlist[k]["targetprice"]) >= buyprice:
                                print(" ===========  buy order sent for ", k, "   ", currlist[k])
                                if mode == "deploy":
                                    # calculate how much can be ordered
                                    baseamount = currlist[k]["entryamount"]
                                    commission = 0.25/100.0
                                    inputbaseamount2 = baseamount - baseamount*commission
                                    inputbaseamount = float(inputbaseamount2)
                                    entryprice = buyprice
                                    currency = "BTC/USDT"
                                    entrytime = self.currenttime()
                                    amount = inputbaseamount/buyprice

                                    currlist[k]["amount"] = float("{:.8f}".format(amount))
                                    currlist[k]["entryamount"] = inputbaseamount
                                    #currlist[k]["entryamount"] = 0.0
                                    
                                    temp_orderbook = pyupbit.get_orderbook(tickers=["USDT-BTC"])
                                    limit_buyprice = temp_orderbook[0]["orderbook_units"][0]["ask_price"]
                                    limit_sellprice = temp_orderbook[0]["orderbook_units"][0]["bid_price"]
                                    temp = upbit.buy_limit_order("USDT-BTC", limit_buyprice, float("{:.8f}".format(inputbaseamount)))

                                    #temp = upbit.buy_market_order("USDT-BTC", float("{:.8f}".format(inputbaseamount)))

                                    bot1= bot2= bot3= bot1info= bot2info= bot3info = ""
                                    if botsettings[0] != None:
                                        bot1 = botsettings[0]
                                    if botsettings[1] != None:
                                        bot2 = botsettings[1]
                                    if botsettings[2] != None:
                                        bot3 = botsettings[2]
                                    if botinfo[0] != None:
                                        bot1info = botinfo[0]
                                    if botinfo[1] != None:
                                        bot2info = botinfo[1]
                                    if botinfo[2] != None:
                                        bot3info = botinfo[2]
                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount, j, k, False, buyprice, sellprice, json.dumps(bot1), json.dumps(bot2), json.dumps(bot3), json.dumps(bot1info), json.dumps(bot2info), json.dumps(bot3info))
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding, buyprice, sellprice, botone, bottwo, botthree, botoneinfo, bottwoinfo, botthreeinfo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                else:
                                    amount = 0.01
                                    currlist[k]["amount"] = float(amount)
                                    currency = "BTC/USDT"
                                    entryprice = buyprice
                                    commission = 0.25
                                    entrytime = self.currenttime()
                                    # baseamount should be based on what's actually filled as well
                                    baseamount = float(currlist[k]["entryamount"])
                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                currlist[k]["entryprice"] = buyprice
                                currlist[k]["entered"] = True
                                currentered = True
                    #print(" new currlist before updating db  ", currlist)
                    if currentered:
                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()


                if botsettings[j]["currpyramiding"] == True:
                    print(" ============ currently pyramiding is True, so pyramiding sendtrade buytrade logic sent")
                    currlist = botinfopyramiding[j]["data"]
                    currentered = False
                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == False:
                            if float(currlist[k]["targetprice"]) < buyprice:
                                print(" ===========  buy order sent for ", k, "   ", currlist[k])
                                if mode == "deploy":
                                    # calculate how much can be ordered
                                    baseamount = currlist[k]["entryamount"]
                                    commission = 0.25/100.0
                                    inputbaseamount2 = baseamount - baseamount*commission
                                    inputbaseamount = float(inputbaseamount2)
                                    entryprice = buyprice
                                    currency = "BTC/USDT"
                                    entrytime = self.currenttime()
                                    amount = inputbaseamount/buyprice

                                    currlist[k]["amount"] = float("{:.8f}".format(amount))
                                    currlist[k]["entryamount"] = inputbaseamount
                                    #currlist[k]["entryamount"] = 0.0
                                    
                                    temp_orderbook = pyupbit.get_orderbook(tickers=["USDT-BTC"])
                                    limit_buyprice = temp_orderbook[0]["orderbook_units"][0]["ask_price"]
                                    limit_sellprice = temp_orderbook[0]["orderbook_units"][0]["bid_price"]
                                    temp = upbit.buy_limit_order("USDT-BTC", limit_buyprice, float("{:.8f}".format(inputbaseamount)))

                                    #temp = upbit.buy_market_order("USDT-BTC", float("{:.8f}".format(inputbaseamount)))

                                    bot1= bot2= bot3= bot1info= bot2info= bot3info = ""
                                    if botsettings[0] != None:
                                        bot1 = botsettings[0]
                                    if botsettings[1] != None:
                                        bot2 = botsettings[1]
                                    if botsettings[2] != None:
                                        bot3 = botsettings[2]
                                    if botinfo[0] != None:
                                        bot1info = botinfo[0]
                                    if botinfo[1] != None:
                                        bot2info = botinfo[1]
                                    if botinfo[2] != None:
                                        bot3info = botinfo[2]
                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount, j, k, False, buyprice, sellprice, json.dumps(bot1), json.dumps(bot2), json.dumps(bot3), json.dumps(bot1info), json.dumps(bot2info), json.dumps(bot3info))
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding, buyprice, sellprice, botone, bottwo, botthree, botoneinfo, bottwoinfo, botthreeinfo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                else:
                                    amount = 0.01
                                    currlist[k]["amount"] = float(amount)
                                    currency = "BTC/USDT"
                                    entryprice = buyprice
                                    commission = 0.25
                                    entrytime = self.currenttime()
                                    # baseamount should be based on what's actually filled as well
                                    baseamount = float(currlist[k]["entryamount"])
                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                currlist[k]["entryprice"] = buyprice
                                currlist[k]["entered"] = True
                                currentered = True
                    #print(" new currlist before updating db  ", currlist)
                    if currentered:
                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

        return "success"



    def selltrade(self, buyprice, sellprice, mode="deploy"):
        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            userid = userlist[i][0]

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
            botsettings = self.dbcur.fetchall()[0]

            if botsettings[0]["active"] == False:
                continue

            apikeys = []
            upbit = []
            if mode == "deploy":
                apikeys = self.dbcur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userlist[i][0],))
                apikeys = self.dbcur.fetchall()[0]
                upbit = Upbit(apikeys[0], apikeys[1])

            maxrange = 0
            for q in range(0, len(botsettings)):
                if botsettings[q]["active"] == True:
                    maxrange
            maxrange += 1

            self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
            botinfo = self.dbcur.fetchall()[0]

            self.dbcur.execute("SELECT botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding FROM botsdata WHERE userid = %s", (userlist[i][0],))
            botinfopyramiding = self.dbcur.fetchall()[0]

            for j in range(0, maxrange):
                
                if botsettings[j]["currpyramiding"] == False:
                    print(" ============ currently pyramiding is False, so downpyramiding sendtrade selltrade logic sent")
                    currlist = botinfo[j]["data"]
                    currentered = False
                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == True:
                            if float(sellprice)/float(currlist[k]["entryprice"])-1.0 >= float(botsettings[j]["percentreturnpyramiding"])/100.0:
                                if mode == "deploy":
                                    print(" ===========  sell order sent for ", k, "   ", currlist[k])
                                    # calculate how much can be ordered
                                    amount = currlist[k]["amount"]
                                    commission = 0.25/100.0
                                    inputamount2 = amount - amount*commission
                                    inputamount = float("{:.8f}".format(inputamount2))
                                    entryprice = sellprice
                                    currency = "BTC/USDT"
                                    entrytime = self.currenttime()
                                    entryamount = inputamount*sellprice
                                    currlist[k]["entryamount"] = entryamount
                                    currlist[k]["amount"] = inputamount

                                    #currlist[k]["entryamount"] = 0.0
                                    
                                    temp_orderbook = pyupbit.get_orderbook(tickers=["USDT-BTC"])
                                    limit_buyprice = temp_orderbook[0]["orderbook_units"][0]["ask_price"]
                                    limit_sellprice = temp_orderbook[0]["orderbook_units"][0]["bid_price"]
                                    temp = upbit.sell_limit_order("USDT-BTC", limit_sellprice, float("{:.8f}".format(inputamount)))

                                    #temp = upbit.buy_market_order("USDT-BTC", float("{:.8f}".format(inputbaseamount)))

                                    bot1= bot2= bot3= bot1info= bot2info= bot3info = ""
                                    if botsettings[0] != None:
                                        bot1 = botsettings[0]
                                    if botsettings[1] != None:
                                        bot2 = botsettings[1]
                                    if botsettings[2] != None:
                                        bot3 = botsettings[2]
                                    if botinfo[0] != None:
                                        bot1info = botinfo[0]
                                    if botinfo[1] != None:
                                        bot2info = botinfo[1]
                                    if botinfo[2] != None:
                                        bot3info = botinfo[2]
                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, entryamount, j, k, False, buyprice, sellprice, json.dumps(bot1), json.dumps(bot2), json.dumps(bot3), json.dumps(bot1info), json.dumps(bot2info), json.dumps(bot3info))
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding, buyprice, sellprice, botone, bottwo, botthree, botoneinfo, bottwoinfo, botthreeinfo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                else:
                                    amount = 0.01
                                    currlist[k]["amount"] = float(amount)
                                    currency = "BTC/USDT"
                                    entryprice = buyprice
                                    commission = 0.25
                                    entrytime = self.currenttime()
                                    # baseamount should be based on what's actually filled as well
                                    baseamount = float(currlist[k]["entryamount"])
                                    tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                currlist[k]["entryprice"] = sellprice
                                currlist[k]["entered"] = False
                                currentered = True
                    #print(" new currlist before updating db  ", currlist)
                    if currentered:
                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                    # if all downpyramiding exited for botone, and pyramiding = False, 
                    # then set firsttrading = True
                    self.dbcur.execute("SELECT botoneinfo FROM botsdata WHERE userid = %s", (userid,))
                    tempbotoneinfo = self.dbcur.fetchall()[0][0]
                    self.dbcur.execute("SELECT botone FROM bots WHERE userid = %s", (userid,))
                    tempbotone = self.dbcur.fetchall()[0][0]
                    isAllExit = True
                    for l in range(0, len(tempbotoneinfo["data"])):
                        if tempbotoneinfo["data"][l]["entered"] == True:
                            isAllExit = False
                    if isAllExit and not tempbotone["pyramiding"]:
                        self.dbcur.execute("UPDATE bots SET firsttrading = %s WHERE userid = %s", (True, userid))
                        self.dbconn.commit()


                if botsettings[j]["currpyramiding"] == True:
                    print(" ============ currently pyramiding is True, so pyramiding sendtrade selltrade logic sent")
                    currlist = botinfopyramiding[j]["data"]
                    currentered = False
                    isAllExit = True
                    for k in range(0, len(currlist)-1):
                        if currlist[k]["entered"] == False:
                            isAllExit = False
                    if currlist[len(currlist)-1]["targetprice"] > sellprice:
                        isAllExit = False

                    if isAllExit:

                        for k in range(0, len(currlist)):
                            if currlist[k]["entered"] == True:
                                print(" ===========  sell order sent for ", k, "   ", currlist[k])
                                if mode == "deploy":
                                    # calculate how much can be ordered
                                    amount = currlist[k]["amount"]
                                    commission = 0.25/100.0
                                    inputamount2 = amount - amount*commission
                                    inputamount = float("{:.8f}".format(inputamount2))
                                    entryprice = sellprice
                                    currency = "BTC/USDT"
                                    entrytime = self.currenttime()
                                    entryamount = inputamount*sellprice
                                    currlist[k]["entryamount"] = entryamount
                                    currlist[k]["amount"] = inputamount

                                    #currlist[k]["entryamount"] = 0.0
                                    
                                    temp_orderbook = pyupbit.get_orderbook(tickers=["USDT-BTC"])
                                    limit_buyprice = temp_orderbook[0]["orderbook_units"][0]["ask_price"]
                                    limit_sellprice = temp_orderbook[0]["orderbook_units"][0]["bid_price"]
                                    temp = upbit.sell_limit_order("USDT-BTC", limit_sellprice, float("{:.8f}".format(inputamount)))

                                    #temp = upbit.buy_market_order("USDT-BTC", float("{:.8f}".format(inputbaseamount)))

                                    bot1= bot2= bot3= bot1info= bot2info= bot3info = ""
                                    if botsettings[0] != None:
                                        bot1 = botsettings[0]
                                    if botsettings[1] != None:
                                        bot2 = botsettings[1]
                                    if botsettings[2] != None:
                                        bot3 = botsettings[2]
                                    if botinfo[0] != None:
                                        bot1info = botinfo[0]
                                    if botinfo[1] != None:
                                        bot2info = botinfo[1]
                                    if botinfo[2] != None:
                                        bot3info = botinfo[2]
                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, entryamount, j, k, False, buyprice, sellprice, json.dumps(bot1), json.dumps(bot2), json.dumps(bot3), json.dumps(bot1info), json.dumps(bot2info), json.dumps(bot3info))
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding, buyprice, sellprice, botone, bottwo, botthree, botoneinfo, bottwoinfo, botthreeinfo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                else:
                                    amount = 0.01
                                    currlist[k]["amount"] = float(amount)
                                    currency = "BTC/USDT"
                                    entryprice = buyprice
                                    commission = 0.25
                                    entrytime = self.currenttime()
                                    # baseamount should be based on what's actually filled as well
                                    baseamount = float(currlist[k]["entryamount"])
                                    tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                currlist[k]["entryprice"] = sellprice
                                currlist[k]["entered"] = False
                                currentered = True
                    #print(" new currlist before updating db  ", currlist)
                    if currentered:
                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        self.dbcur.execute("UPDATE bots SET firsttrading = %s WHERE userid = %s", (True, userid))
                        self.dbconn.commit()


                    #temptemp = pyramiding(self.dbcur, self.dbconn)
                    #result = temptemp.updates(buyprice, sellprice)


        return "success"

