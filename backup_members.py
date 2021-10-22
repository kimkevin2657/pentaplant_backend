
import random
import numpy as np
import asyncio 
import time
from datetime import datetime as dt
from datetime import date, timedelta
import json
import requests
import psycopg2
from upbitapi import upbitapi

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

            self.dbcur.execute("SELECT firsttrading FROM bots WHERE userid = %s", (userlist[i][0],))
            firsttrading = self.dbcur.fetchall()[0]

            # skips over the user whose first bot range is deactivated
            if botsettings[0]["active"] == False:
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                maxrange = 0
                for r in range(0, len(botsettings)):
                    if botsettings[r]["active"] == True:
                        maxrange = r
                
                # botinfo[0] = botoneinfo
                # botinfo[0][0] = botoneinfo[0]
                # if the currentprice is less than the highest target price, then skip
                if not firsttrading[0]:
                    if botinfo[0]["data"][0]["baseprice"] > buyprice:

                        continue
                else:

                    bottomprice = buyprice

                    for j in range(0, len(botsettings)):

                        ### checking to see if the current bot range is in pyramiding or not
                        ### updated october 7th
                        if not firsttrading[0]:
                            if botsettings[j]["currpyramiding"] == True:
                                continue

                        if botsettings[j]["active"] == False:
                            continue
                        else:

                            if firsttrading[0]:
                                upapi = upbitapi()
                                total_balance = upapi.total_balance(userlist[i][0],self.dbcur)
                                if total_balance[0] > 0 and total_balance[1] < 1:
                                    tempamount = upapi.buy_usdt(userlist[i][0],self.dbcur)
                                    botsettings[j]["amount"] = tempamount
                                if total_balance[1] > 10:
                                    botsettings[j]["amount"] = total_balance[1]


                            entryamount = float(botsettings[j]["amount"])*(1.0/float(botsettings[j]["entrynum"]))
                            dollar_difference = float(buyprice)*(float(botsettings[j]["percentrange"])/100.0)*(1.0/float(botsettings[j]["entrynum"]))
                            
                            botsettings[j]["pricediff"] = dollar_difference

                            bottomprice += dollar_difference + 0.01
                            
                            templist = []
                            for k in range(0, botsettings[j]["entrynum"]):
                                currtarget = bottomprice - dollar_difference
                                # should "entryprice" be currtarget vs currentprice?
                                if k == 0:
                                    templist.append({"targetprice": currtarget, "entryprice": currtarget, "entryamount": entryamount, "entered": False, "baseprice": buyprice, "amount": 0})
                                else:
                                    templist.append({"targetprice": currtarget, "entryprice": currtarget, "entryamount": entryamount, "entered": False, "amount": 0})
                                bottomprice = currtarget


                            if j == 0:
                                self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                                self.dbconn.commit()

                            if j == 1:
                                self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                                self.dbconn.commit()
                            if j == 2:
                                self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userlist[i][0]))
                                self.dbconn.commit()

                            if j == 0:
                                self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                                self.dbconn.commit()

                            if j == 1:
                                self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                                self.dbconn.commit()
                            if j == 2:
                                self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                                self.dbconn.commit()



            #self.dbcur.execute("UPDATE bots SET firsttrading = %s WHERE userid = %s", (False, userlist[i][0]))
            #self.dbconn.commit()

        return "success"

