
import random
import numpy as np
import asyncio 
import time
from datetime import datetime as dt
from datetime import date, timedelta
import json
import requests
import psycopg2

class members:
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
            if botsettings[0]["active"] == False:
                print()
                print(" update method skipped user ", userlist[i][0], " due to all bots inactive")
                print()
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]
                
                # botinfo[0] = botoneinfo
                # botinfo[0][0] = botoneinfo[0]
                # if the currentprice is less than the highest target price, then skip
                if botinfo[0]["data"][0]["targetprice"] > buyprice:
                    print()
                    print(" update method skipped user ", userlist[i][0], " since the buy price not greater than the current highest price ")
                    print()
                    continue
                else:

                    bottomprice = buyprice


                    for j in range(0, len(botsettings)):
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
                                    templist[k]["entered"] = botinfo[2]["data"][k]["entered"]
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

