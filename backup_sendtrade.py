
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

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]


            if botsettings[0]["active"] == False:

                continue
            else:

                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                apikeys = []
                upbit = []
                if mode == "deploy":
                    apikeys = self.dbcur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userlist[i][0],))
                    apikeys = self.dbcur.fetchall()[0]

                    upbit = Upbit(apikeys[0], apikeys[1])

                
                maxrange = 0
                for r in range(0, len(botinfo)):
                    if botinfo[r] == None:
                        maxrange = r
                        break
                    else:
                        maxrange = r

                for j in range(0, maxrange):

                    if botsettings[j]["currpyramiding"] == True:
                        continue

                    currlist = botinfo[j]["data"]

                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == False:
                            if float(currlist[k]["targetprice"]) >= buyprice:

                            
                                # execute trade with the amount currlist[k]["entryamount"]
                                # trade code

                                # insert into transaction database
                                # transaction code
                                # id, userid, side, amount (in target coins) , currency, entryprice, commission, entrytime, baseamount (in base currency) 

                                if mode == "deploy":
                                    # calculate how much can be ordered



                                    baseamount = currlist[k]["entryamount"]
                                    commission = 0.25/100.0
                                    inputbaseamount2 = baseamount - baseamount*commission
                                    inputbaseamount = float("{:.2f}".format(inputbaseamount2))
                                    entryprice = buyprice
                                    currency = "BTC/USDT"
                                    entrytime = self.currenttime()
                                    amount = inputbaseamount/buyprice

                                    currlist[k]["amount"] = float("{:.4f}".format(amount))
                                    currlist[k]["entryamount"] = 0.0
                                    
                                    temp = upbit.buy_market_order("USDT-BTC", inputbaseamount)

                                    tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount, j, k, False)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                else:
                                    amount = 0.01
                                    currlist[k]["amount"] = float("{:.4f}".format(amount))
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


                    print(" new currlist before updating db  ", currlist)
                    if j == 0:

                        self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

                    if j == 1:

                        self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:

                        self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    

        return "success"

    def selltrade(self, buyprice, sellprice, mode="deploy"):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            
            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]

            if botsettings[0]["active"] == False:
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                apikeys = self.dbcur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userlist[i][0],))
                apikeys = self.dbcur.fetchall()[0]

                upbit = Upbit(apikeys[0], apikeys[1])

                maxrange = 0
                for r in range(0, len(botinfo)):
                    if botinfo[r] == None:
                        maxrange = r
                        break
                    else:
                        maxrange = r

                for j in range(0, maxrange):

                    if botsettings[j]["currpyramiding"] == True:
                        continue
                    
                    currlist = botinfo[j]["data"]

                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == True:
                            if sellprice/float(currlist[k]["entryprice"]) - 1.0 > float(botsettings[j]["percentreturn"])/100.0:
                                #currlist[k]["entryprice"] = sellprice
                                currlist[k]["entryprice"] = 0
                                currlist[k]["entered"] = False
                                
                                # execute trade with the amount currlist[k]["entryamount"]
                                # trade code

                                # insert into transaction database
                                # transaction code
                                # id, userid, side, amount (in target coins) , currency, entryprice, commission, entrytime, baseamount (in base currency) 

                                if mode == "deploy":
                                    baseamount = currlist[k]["amount"]
                                    commission = 0.25/100.0
                                    inputbaseamount = float("{:.4f}".format(baseamount))
                                    entryprice = sellprice
                                    currency = "BTC/USDT"
                                    entrytime = self.currenttime()
                                    amount = sellprice*inputbaseamount - sellprice*inputbaseamount*commission
                                    entryamount = float("{:.2f}".format(sellprice*amount))

                                    currlist[k]["amount"] = 0.0
                                    currlist[k]["entryamount"] = entryamount

                                    temp = upbit.sell_market_order("USDT-BTC", amount)

                                    tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount, j, k, False)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()
                                else:
                                    amount = 0.01
                                    currency = "BTC/USDT"
                                    entryprice = sellprice
                                    commission = 0.25
                                    entrytime = self.currenttime()
                                    baseamount = currlist[k]["entryamount"]
                                    tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount,j,k,True)
                                    self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount, range, rangeindex, pyramiding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                    self.dbconn.commit()


                    if j == 0:
                        self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

                    if j == 1:
                        self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:
                        self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

        return "success"


