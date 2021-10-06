
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
        print()
        print(" buytrade method executed ")
        print()

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]


            if botsettings[0]["active"] == False:
                print()
                print(" skipped user ", userlist[i][0], " due to all bots inactive")
                print()
                continue
            else:
                print()
                print(" user not skipped ", userlist[i][0], " due to all bots active")
                print()
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                for j in range(0, len(botinfo)):
                    currlist = botinfo[j]["data"]

                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == False:
                            if currlist[k]["targetprice"] >= buyprice:
                                print()
                                print(" userid  ", userlist[i][0], "  trading bot  ", j, "   for ",k,"'th range ", buyprice, "  ", currlist[k]["targetprice"])
                                print()
                                currlist[k]["entryprice"] = buyprice
                                currlist[k]["entered"] = True
                                print()
                                print(" new currlist for userid ", userlist[i][0], " trading bot " , j , " for ",k,"'th range ")
                                print(currlist)
                                print()

                                # execute trade with the amount currlist[k]["entryamount"]
                                # trade code

                                # insert into transaction database
                                # transaction code
                                # id, userid, side, amount (in target coins) , currency, entryprice, commission, entrytime, baseamount (in base currency) 
                                amount = 0.01
                                currency = "BTC/USDT"
                                entryprice = buyprice
                                commission = 0.25
                                entrytime = self.currenttime()
                                # baseamount should be based on what's actually filled as well
                                baseamount = currlist[k]["entryamount"]
                                tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount)
                                self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                self.dbconn.commit()

                    print(" new currlist before updating db  ", currlist)
                    if j == 0:
                        print()
                        print(" userid ", userlist[i][0], " tradingbot ", j, " updated")
                        print()
                        self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

                        self.dbcur.execute("SELECT botoneinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                        temp = self.dbcur.fetchall()
                        print(" ===============   ", temp)

                    if j == 1:
                        print()
                        print(" userid ", userlist[i][0], " tradingbot ", j, " updated")
                        print()
                        self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:
                        print()
                        print(" userid ", userlist[i][0], " tradingbot ", j, " updated")
                        print()
                        self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    

        return "success"

    def selltrade(self, buyprice, sellprice, mode="deploy"):
        print()
        print(" selltrade method executed ")
        print()

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

                for j in range(0, len(botinfo)):
                    currlist = botinfo[j]["data"]

                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == True:
                            if sellprice/currlist[k]["entryprice"] - 1.0 > float(botsettings[j]["percentreturn"])/100.0:
                                currlist[k]["entryprice"] = sellprice
                                currlist[k]["entered"] = False
                                
                                # execute trade with the amount currlist[k]["entryamount"]
                                # trade code

                                # insert into transaction database
                                # transaction code
                                # id, userid, side, amount (in target coins) , currency, entryprice, commission, entrytime, baseamount (in base currency) 
                                amount = 0.01
                                currency = "BTC/USDT"
                                entryprice = sellprice
                                commission = 0.25
                                entrytime = self.currenttime()
                                baseamount = currlist[k]["entryamount"]
                                tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount)
                                self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)


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


