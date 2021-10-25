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

            if j == 0:
                self.dbcur.execute("SELECT botone FROM bots WHERE userid = %s", (userid,))
                currbot = self.dbcur.fetchall()[0][0]
                currbot["currpyramiding"] = False
                self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(currbot), userid))
                self.dbconn.commit()
            if j == 1:
                self.dbcur.execute("SELECT bottwo FROM bots WHERE userid = %s", (userid,))
                currbot = self.dbcur.fetchall()[0][0]
                currbot["currpyramiding"] = False
                self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(currbot), userid))
                self.dbconn.commit()
            if j == 2:
                self.dbcur.execute("SELECT botthree FROM bots WHERE userid = %s", (userid,))
                currbot = self.dbcur.fetchall()[0][0]
                currbot["currpyramiding"] = False
                self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(currbot), userid))
                self.dbconn.commit()

        for j in range(0, len(botsettings)):
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

                self.update.updatepyramiding(userid, botpyramiding["data"][0]["baseprice"], j)



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


            maxrange = 0
            for j in range(0, len(botsettings)):
                if botsettings[j]["active"] == True:
                    maxrange = j


            self.dbcur.execute("SELECT botactive FROM users WHERE userid = %s", (userid,))
            botactive = self.dbcur.fetchall()[0][0]
            
            if not botactive:
                continue

            if firsttrading:

                self.initialize(userid, buyprice, botsettings)

            if not firsttrading:

                # if all downpyramiding is exited and pyramiding = False
                # , then self.update.updates, and self.update.updatepyramiding again
                downpyramidingexited = True
                nopyramiding = True
                if botsettings[0]["pyramiding"] == True:
                    nopyramiding = False
                for q in range(0, len(botoneinfo["data"])):
                    if botoneinfo["data"][q]["entered"] == True:
                        downpyramidingexited = False
                for q in range(0, len(bottwoinfo["data"])):
                    if bottwoinfo["data"][q]["entered"] == True:
                        downpyramidingexited = False
                for q in range(0, len(botthreeinfo["data"])):
                    if botthreeinfo["data"][q]["entered"] == True:
                        downpyramidingexited = False
                
                if downpyramidingexited and nopyramiding and buyprice > botoneinfo["data"][0]["baseprice"]:

                    self.initialize(userid, buyprice, botsettings)


                # if only one downpyramiding entered and sell price > baseprice, 
                # then set currpyramiding = True if pyramiding = True
                # then change one'th pyramiding to entered = True, set entryamount, amount
                # then change one'th downpyramiding to entered = False, entryamount = 0, amount = 0


                # if some pyramiding is entered and buy price < baseprice, 
                # then set currpyramiding = False if pyramiding = True
                for j in range(0, maxrange):
                    pyramidingentered = False
                    for q in range(0, len(botinfopyramiding[j]["data"])):
                        if botinfopyramiding[j]["data"][q]["entered"] == True:
                            pyramidingentered = True
                    if pyramidingentered and botsettings[j]["pyramiding"] == True and botsettings[j]["currpyramiding"] == True and buyprice < botinfopyramiding[j]["data"][0]["baseprice"]:
                        pyramidingcount = 0
                        for q in range(0, len(botinfopyramiding[j]["data"])):
                            if botinfopyramiding[j]["data"][q]["entered"] == True:
                                pyramidingcount = q
                        pyramidingcount += 1

                        for q in range(0, pyramidingcount):
                            botinfo[j]["data"][q]["amount"] = botinfopyramiding[j]["data"][q]["amount"]
                            botinfo[j]["data"][q]["entered"] = True
                            botinfo[j]["data"][q]["entryprice"] = botinfopyramiding[j]["data"][q]["entryprice"]
                            botinfo[j]["data"][q]["entryamount"] = botinfopyramiding[j]["data"][q]["entryamount"]
                            if q == 0:
                                botinfo[j]["data"][q]["baseprice"] = botinfopyramiding[j]["data"][q]["baseprice"]
                            
                        self.update.updatepyramiding(userid, botinfo[j]["data"][0]["baseprice"], j)
                        
                        if j == 0:
                            self.dbcur.execute("SELECT botone FROM bots WHERE userid = %s", (userid,))
                            tempbot = self.dbcur.fetchall()[0][0]
                            tempbot["currpyramiding"] = False
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(tempbot), userid))
                            self.dbconn.commit()

                            self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()

                        if j == 1:
                            self.dbcur.execute("SELECT bottwo FROM bots WHERE userid = %s", (userid,))
                            tempbot = self.dbcur.fetchall()[0][0]
                            tempbot["currpyramiding"] = False
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(tempbot), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("SELECT botthree FROM bots WHERE userid = %s", (userid,))
                            tempbot = self.dbcur.fetchall()[0][0]
                            tempbot["currpyramiding"] = False
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(tempbot), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()

                        




































