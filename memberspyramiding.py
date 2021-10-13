
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

            self.dbcur.execute("SELECT firsttrading FROM bots WHERE userid = %s", (userlist[i][0],))
            firsttrading = self.dbcur.fetchall()[0]

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

                    # skips if the currpyramiding is false
                    """
                    if not firsttrading[0]:
                        if botsettings[j]["currpyramiding"] == False:
                            continue
                    """

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

                    tempbool2 = False
                    for k in range(0, len(botinfopyramiding[j])):
                        if botinfopyramiding[j]["data"][k]["entered"] == True:
                            tempbool2 = True
                        if tempbool2:
                            break

                    # if all ranges in the given bot is not entered
                    if not tempbool and not tempbool2:
                        
                        # then updates the pyramiding bot info

                        entrynum = int(botsettings[j]["entrynumpyramiding"])

                        precentreturnpyramiding = float(botsettings[j]["percentreturnpyramiding"])
                        totalentryamount = 0.0
                        for k in range(0, len(botinfo[j]["data"])):
                            totalentryamount += float(botinfo[j]["data"][k]["entryamount"])

                        
                        entryamount = totalentryamount*(1.0/float(entrynum))

                        bottomprice = float(botinfo[j]["data"][0]["baseprice"])

                        
                        templist = []
                        for k in range(0, entrynum):
                            currtarget = bottomprice*(1.0+precentreturnpyramiding/100.0)
                            if k == 0:
                                templist.append({"targetprice": currtarget, "entryprice": buyprice, "entryamount": entryamount, "entered": False, "baseprice": bottomprice})
                            else:
                                templist.append({"targetprice": currtarget, "entryprice": buyprice, "entryamount": entryamount, "entered": False})
                            bottomprice = currtarget

                        if j == 0:
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                            self.dbconn.commit()

            self.dbcur.execute("UPDATE bots SET firsttrading = %s WHERE userid = %s", (False, userlist[i][0]))
            self.dbconn.commit()

        return "success"    