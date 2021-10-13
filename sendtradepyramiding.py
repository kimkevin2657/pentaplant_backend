
import random
import numpy as np
import asyncio 
import time
import json
import requests
import psycopg2

from members import members
from memberspyramiding import memberspyramiding

from time import gmtime, strftime
import datetime
import pytz

class sendtradepyramiding:
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

        print(" ======  sendtradepyramiding ")

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            print(" === user idex " , i)

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]

            print(" === botsettings ", 0 , " ", json.dumps(botsettings[0],indent=4))
            print(" === botsettings ", 1 , " ", json.dumps(botsettings[1],indent=4))
            print(" === botsettings ", 2 , " ", json.dumps(botsettings[2],indent=4))

            if botsettings[0]["active"] == False:
                print(" === skipping over since all bots are inactive" )
                continue
            else:

                #self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                self.dbcur.execute("SELECT botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                print(" === botinfo ", 0 , " ", json.dumps(botinfo[0],indent=4))
                print(" === botinfo ", 1 , " ", json.dumps(botinfo[1],indent=4))
                print(" === botinfo ", 2 , " ", json.dumps(botinfo[2],indent=4))

                for j in range(0, len(botinfo)):


                    if botsettings[j]["currpyramiding"] == False:
                        print(" === skipping over this bot since the currpyramiding is False ")
                        continue


                    currlist = botinfo[j]["data"]

                    # checks whether the pyramiding exit range has been reached before entering a possible new trade
                    passedpyramidingexit = False
                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == True and k == int(botsettings[j]["pyramidingexit"])-1:
                            passedpyramidingexit = True

                    print(" passedpyramiding ", passedpyramidingexit)

                    if passedpyramidingexit:
                        if j == 0:
                            botsettings[0]["passedpyramidingexit"] = True
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[0]), userlist[i][0]))
                            self.dbconn.commit()

                        if j == 1:
                            botsettings[0]["passedpyramidingexit"] = True
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[0]), userlist[i][0]))
                            self.dbconn.commit()

                        if j == 2:
                            botsettings[0]["passedpyramidingexit"] = True
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[0]), userlist[i][0]))
                            self.dbconn.commit()


                    for k in range(0, len(currlist)-1):
                        if currlist[k]["entered"] == False:
                            #if currlist[k]["targetprice"] >= buyprice:
                            if float(currlist[k]["targetprice"]) <= buyprice:

                                currlist[k]["entryprice"] = buyprice
                                currlist[k]["entered"] = True

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
                                baseamount = float(currlist[k]["entryamount"])
                                tupleval = (userlist[i][0], "buy", amount, currency, entryprice, commission, entrytime, baseamount)
                                self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                self.dbconn.commit()

                    print(" new currlist before updating db  ", currlist)
                    if j == 0:

                        #self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

                    if j == 1:

                        #self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:

                        #self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
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
                #self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                self.dbcur.execute("SELECT botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinforegular = self.dbcur.fetchall()[0]

                for j in range(0, len(botinfo)):

                    if botsettings[j]["currpyramiding"] == False:
                        continue

                    membersobj = members(self.dbcur, self.dbconn)
                    memberspyramidingobj = memberspyramiding(self.dbcur,self.dbconn)

                    currlist = botinfo[j]["data"]

                    # liquidate all open positions once the sell price exceeds the most top level pyramiding price
                    all_liquidate_price = currlist[-1]["targetprice"]
                    if sellprice >= all_liquidate_price:

                        # liquidate all open positions
                        for k in range(0, len(currlist)):
                            if currlist[k]["entered"] == True:
                                currlist[k]["entryprice"] = 0
                                currlist[k]["entered"] = False

                                amount = 0.01
                                currency = "BTC/USDT"
                                entryprice = sellprice
                                commission = 0.25
                                entrytime = self.currenttime()
                                baseamount = currlist[k]["entryamount"]
                                tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount)
                                self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                self.dbconn.commit()

                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                        result = membersobj.update(buyprice, sellprice)
                        result = memberspyramidingobj.update(buyprice, sellprice)

                        botsettings[j]["currpyramiding"] = False
                        print(" botsettings ", j , "  ", json.dumps(botsettings[j],indent=4))
                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()


                    # liquidate all open positions once the sell price is below the pyramidingexit range
                    setting_liquidate_price = int(botsettings[j]["pyramidingexit"])
                    print(" setting liquidation index  ", setting_liquidate_price)
                    setting_liquidate_price = float(botinfo[j]["data"][setting_liquidate_price-1]["entryprice"])
                    print(" setting liquidation price  ", setting_liquidate_price)
                    print(" passedpyramidingexit  ", botsettings[j]["passedpyramidingexit"])
                    if setting_liquidate_price > sellprice and botsettings[j]["passedpyramidingexit"]:
                    #if setting_liquidate_price <= sellprice:
                        
                        # liquidate all open positions
                        for k in range(0, len(currlist)):
                            if currlist[k]["entered"] == True:
                                currlist[k]["entryprice"] = 0
                                currlist[k]["entered"] = False

                                amount = 0.01
                                currency = "BTC/USDT"
                                entryprice = sellprice
                                commission = 0.25
                                entrytime = self.currenttime()
                                baseamount = currlist[k]["entryamount"]
                                tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount)
                                self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                self.dbconn.commit()


                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                        result = membersobj.update(buyprice, sellprice)
                        result = memberspyramidingobj.update(buyprice, sellprice)

                        botsettings[j]["currpyramiding"] = False
                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()

                    # liquidate all open positions once the sell price reaches the baseprice for regular range
                    if sellprice <= float(botinforegular[j]["data"][0]["baseprice"]):

                        # liquidate all open positions
                        for k in range(0, len(currlist)):
                            if currlist[k]["entered"] == True:
                                currlist[k]["entryprice"] = 0
                                currlist[k]["entered"] = False

                                amount = 0.01
                                currency = "BTC/USDT"
                                entryprice = sellprice
                                commission = 0.25
                                entrytime = self.currenttime()
                                baseamount = currlist[k]["entryamount"]
                                tupleval = (userlist[i][0], "sell", amount, currency, entryprice, commission, entrytime, baseamount)
                                self.dbcur.execute("INSERT INTO transaction (userid, side, amount, currency, entryprice, commission, entrytime, baseamount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",tupleval)
                                self.dbconn.commit()

                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                            self.dbconn.commit()

                        result = membersobj.update(buyprice, sellprice)
                        result = memberspyramidingobj.update(buyprice, sellprice)


                        botsettings[j]["currpyramiding"] = False
                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]),userlist[i][0]))
                            self.dbconn.commit()
                    

                    

        return "success"