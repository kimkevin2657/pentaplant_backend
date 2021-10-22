import random
import numpy as np
import asyncio 
import time
from datetime import datetime as dt
from datetime import date, timedelta
import json
import requests
import psycopg2
from update import update

class pyramiding:
    def __init__(self, dbcur, dbconn):
        self.dbcur = dbcur
        self.dbconn = dbconn
        self.update = update()

    def initialize(self, userid, buyprice, botsettings):
        self.update.updates(userid, buyprice)
        for j in range(0, len(botsettings)):
            if botsettings[j]["active"] == False:
                continue

            maxrange = 0
            for q in range(0, len(botsettings)):
                if botsettings[q]["active"] == True:
                    maxrange = q
            for q in range(0, maxrange):
                if q == 0:
                    self.dbcur.execute("SELECT botone FROM bots WHERE userid = %s", (userid,))
                    currbot = self.dbcur.fetchall()[0][0]
                    currbot["currpyramiding"] = False
                    self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(currbot), userid))
                    self.dbconn.commit()
                if q == 1:
                    self.dbcur.execute("SELECT bottwo FROM bots WHERE userid = %s", (userid,))
                    currbot = self.dbcur.fetchall()[0][0]
                    currbot["currpyramiding"] = False
                    self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(currbot), userid))
                    self.dbconn.commit()
                if q == 2:
                    self.dbcur.execute("SELECT botthree FROM bots WHERE userid = %s", (userid,))
                    currbot = self.dbcur.fetchall()[0][0]
                    currbot["currpyramiding"] = False
                    self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(currbot), userid))
                    self.dbconn.commit()

            if botsettings[j]["pyramiding"] == True:
                botpyramiding = ""
                if j == 0:
                    self.dbcur.execute("SELECT botoneinfo FROM botsdata WHERE userid = %s", (userid,))
                    botpyramiding = self.dbcur.fetchall()[0][0]
                if j == 1:
                    self.dbcur.execute("SELECT bottwoinfo FROM botsdata WHERE userid = %s", (userid,))
                    botpyramiding = self.dbcur.fetchall()[0][0]
                if j == 2:
                    self.dbcur.execute("SELECT botthreeinfo FROM botsdata WHERE userid = %s", (userid,))
                    botpyramiding = self.dbcur.fetchall()[0][0]

                self.update.updatepyramiding(userid, botpyramiding[0]["baseprice"], j)


    def update(self, buyprice, sellprice):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            userid = userlist[i][0]

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
            botsettings = self.dbcur.fetchall()[0]
            botone = botsettings[0]
            bottwo = botsettings[1]
            botthree = botsettings[2]

            self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo, botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding, firsttrading FROM botsdata WHERE userid = %s", (userid,))
            temp = self.dbcur.fetchall()[0]
            botinfo = temp[:3]
            botoneinfo = temp[0]
            bottwoinfo = temp[1]
            botthreeinfo = temp[2]
            botinfopyramiding = temp[3:6]
            botoneinfopyramiding = temp[3]
            bottwoinfopyramiding = temp[4]
            botthreeinfopyramiding = temp[5]
            firsttrading = temp[6]

            self.dbcur.execute("SELECT botactive FROM users WHERE userid = %s", (userid,))
            botactive = self.dbcur.fetchall()[0][0]
            
            if not botactive:
                continue

            if firsttrading:

                self.initialize(userid, buyprice, botsettings)

            if not firsttrading:

                # if all downpyramiding is exited and currpyramiding = False
                # , then self.update.updates, and self.update.updatepyramiding again
                downpyramidingexited = True
                nopyramiding = True
                for q in range(0, len(botsettings)):
                    if botsettings[q]["currpyramiding"] == True:
                        nopyramiding = False
                for q in range(0, len(botoneinfo)):
                    if botoneinfo[q]["entered"] == True:
                        downpyramidingexited = False
                for q in range(0, len(bottwoinfo)):
                    if bottwoinfo[q]["entered"] == True:
                        downpyramidingexited = False
                for q in range(0, len(botthreeinfo)):
                    if botthreeinfo[q]["entered"] == True:
                        downpyramidingexited = False
                
                if downpyramidingexited and nopyramiding:

                    self.initialize(userid, buyprice, botsettings)


                # if only one downpyramiding entered and price > baseprice, 
                # then set currpyramiding = True if pyramiding = True
                # then change one'th pyramiding to entered = True, set entryamount, amount
                # then change one'th downpyramiding to entered = False, entryamount = 0, amount = 0
                onlyone = False
                if botoneinfo[0]["entered"] == True:
                    onlyone = True
                for q in range(1, len(botoneinfo)):
                    if botoneinfo[q]["entered"] == True:
                        onlyone = False
                if onlyone and sellprice > botoneinfo[0]["baseprice"] and botsettings[0]["pyramiding"] == True:
                    self.dbcur.execute("SELECT botone FROM bots WHERE userid = %s", (userid,))
                    tempbot = self.dbcur.fetchall()[0][0]
                    tempbot["currpyramiding"] = True
                    self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(tempbot), userid))
                    self.dbconn.commit()

                    # then change one'th pyramiding to entered = True, set entryamount, amount

                    {
                        "amount": 0.10991256,
                        "entered": true,
                        "baseprice": 62417.66,
                        "entryprice": 62390.369,
                        "entryamount": 0,
                        "targetprice": 62417.67
                    }
                            {
                                "amount": 0,
                                "entered": false,
                                "baseprice": 62417.66,
                                "entryprice": 62390.369,
                                "entryamount": 87095203.10862637,
                                "targetprice": 62729.7483
                            }

                    self.dbcur.execute("SELECT botoneinfopyramiding FROM botsdata WHERE userid = %s", (userid,))
                    tempbot = self.dbcur.fetchall()[0][0]
                    tempbot[0]["entered"] = True
                    tempbot[0]["amount"] = botoneinfo[0]["amount"]
                    tempbot[0]["entryamount"] = botoneinfo[0]["entryamount"]
                    




                    # then change one'th downpyramiding to entered = False, entryamount = 0, amount = 0



                # if no downpyramiding entered and some pyramiding entered and sellprice < baseprice, 
                # then set currpyramiding = False if pyramiding = True
                # convert botinfopyramiding to botinfo 








































