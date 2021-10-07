
import random
import numpy as np
import asyncio 
import time
from datetime import datetime as dt
from datetime import date, timedelta
import json
import requests
import psycopg2

class memberspyramiding:
    def __init__(self, dbcur, dbconn):
        self.dbcur = dbcur
        self.dbconn = dbconn


    def update(self, buyprice, sellprice):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]

            # skips over the user whose first bot range is deactivated
            # which means all the bots are disabled
            if botsettings[0]["active"] == False:
                continue
            else:

                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                self.dbcur.execute("SELECT botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfopyramiding = self.dbcur.fetchall()[0]

                for j in range(0, len(botinfo)):

                    # skips of the bot where pyramiding is not turned on
                    if botsettings[j]["pyramiding"] == False:
                        continue

                    # skips over the bot where the bot active is false
                    if botsettings[j]["active"] == False:
                        continue

                    # checks whether the given bot is all not entered
                    tempbool = False
                    for k in range(0, len(botinfo[j])):
                        if botinfo[j]["data"][k]["entered"] == True:
                            tempbool = True
                        if tempbool:
                            break

                    # if all ranges in the given bot is not entered
                    if not tempbool:
                        
                        # then updates the pyramiding bot info

                        entrynum = botsettings[j]["entrynumpyramiding"]
                        precentreturnpyramiding = float(botsettings[j]["precentreturnpyramiding"])
                        totalentryamount = 0.0
                        for k in range(0, len(botinfo[j]["data"])):
                            totalentryamount += float(botinfo[j]["data"][k]["entryamount"])

                        entryamount = totalentryamount*(1.0/float(entrynum))

                        bottomprice = botinfo[j][]


                        
                        templist = []
                        for k in range(0, entrynum):
                            bottomprice *= (1.0+precentreturnpyramiding/100.0)
                            templist.append({"targetprice": bottomprice, "entryprice": buyprice, "entryamount": entryamount, "entered": False})

                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                            self.dbconn.commit()

                
                # botinfo[0] = botoneinfo
                # botinfo[0][0] = botoneinfo[0]
                # if the currentprice is less than the highest target price, then skip
                if botinfo[0]["data"][0]["targetprice"] > buyprice:

                    continue
                else:

                    bottomprice = buyprice

                    for j in range(0, len(botsettings)):

                        ### checking to see if the current bot range is in pyramiding or not
                        ### updated october 7th
                        if botsettings[j]["currpyramiding"] == True:
                            continue
                        
                        if botsettings[j]["active"] == False:
                            continue
                        else:

                            entryamount = float(botsettings[j]["amount"])*(1.0/float(botsettings[j]["entrynum"]))
                            dollar_difference = float(buyprice)*(float(botsettings[j]["percentrange"])/100.0)*(1.0/float(botsettings[j]["entrynum"]))
                            
                            
                            templist = []
                            for k in range(0, botsettings[j]["entrynum"]):
                                currtarget = bottomprice - dollar_difference
                                # should "entryprice" be currtarget vs currentprice?
                                templist.append({"targetprice": currtarget, "entryprice": currtarget, "entryamount": entryamount, "entered": False})
                                bottomprice = currtarget


                            """
                            if j == 0:
                                for k in range(0, len(templist)):
                                    templist[k]["entryprice"] = botinfo[0]["data"][k]["entryprice"]
                                    templist[k]["entryamount"] = botinfo[0]["data"][k]["entryamount"]
                                    templist[k]["entered"] = botinfo[0]["data"][k]["entered"]

                            if j == 1:
                                for k in range(0, len(templist)):
                                    templist[k]["entryprice"] = botinfo[1]["data"][k]["entryprice"]
                                    templist[k]["entryamount"] = botinfo[1]["data"][k]["entryamount"]
                                    templist[k]["entered"] = botinfo[1]["data"][k]["entered"]

                            if j == 2:
                                for k in range(0, len(templist)):
                                    templist[k]["entryprice"] = botinfo[2]["data"][k]["entryprice"]
                                    templist[k]["entryamount"] = botinfo[2]["data"][k]["entryamount"]
                                    templist[k]["entered"] = botinfo[2]["data"][k]["entered"]s
                            """

                            if j == 0:
                                self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                                self.dbconn.commit()

                            if j == 1:
                                self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                                self.dbconn.commit()
                            if j == 2:
                                self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                                self.dbconn.commit()

        return "success"