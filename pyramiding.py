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
        self.update = update(self.dbcur, self.dbconn)

    def initialize(self, userid, buyprice, botsettings):

        self.update.updates(userid, buyprice)

        for j in range(0, len(botsettings)):
            if botsettings[j]["active"] == False:
                continue

            if j == 0:
                currbot = botsettings[0]
                currbot["currpyramiding"] = False
                self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(currbot), userid))
                self.dbconn.commit()
            if j == 1:
                currbot = botsettings[1]
                currbot["currpyramiding"] = False
                self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(currbot), userid))
                self.dbconn.commit()
            if j == 2:
                currbot = botsettings[2]
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
        
        return "success"



    def updates(self, buyprice, sellprice):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            userid = userlist[i][0]

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
            botsettings = self.dbcur.fetchall()[0]
            botone = botsettings[0]
            bottwo = botsettings[1]
            botthree = botsettings[2]

            self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo, botoneinfopyramiding, bottwoinfopyramiding, botthreeinfopyramiding FROM botsdata WHERE userid = %s", (userid,))
            temp = self.dbcur.fetchall()[0]
            botinfo = temp[:3]
            botoneinfo = temp[0]
            bottwoinfo = temp[1]
            botthreeinfo = temp[2]
            botinfopyramiding = temp[3:6]
            botoneinfopyramiding = temp[3]
            bottwoinfopyramiding = temp[4]
            botthreeinfopyramiding = temp[5]

            self.dbcur.execute("SELECT firsttrading FROM bots WHERE userid = %s", (userid,))
            firsttrading = self.dbcur.fetchall()[0][0]

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

                self.dbcur.execute("UPDATE bots SET firsttrading = %s WHERE userid = %s", (False, userid))
                self.dbconn.commit()

            if not firsttrading:
                print(" ========  not firsttrading for pyramiding.py ")
                # if all exited, and no pyramiding bots, and buyprice > highest price 
                # then self.initialize again
                nopyramiding = True
                if botsettings[0]["pyramiding"] == True:
                    nopyramiding = False

                maxrange = 0
                for q in range(0, len(botsettings)):
                    if botsettings[q]["active"] == True:
                        maxrange = q
                downpyramidingexited = True
                for q in range(0, maxrange+1):
                    for k in range(0, len(botinfo[q]["data"])):
                        if botinfo[q]["data"][k]["entered"] == True:
                            downpyramidingexited = False

                if downpyramidingexited and nopyramiding and buyprice > botoneinfo["data"][0]["baseprice"]:
                    print(" ==========   all downpyramiding exited ,  no pyramiding bots, and buyprice > highest price , therefore self.initialize again ")
                    self.initialize(userid, buyprice, botsettings)



                # if pyramiding is entered, buy price < base price for that pyramiding
                # then set currpyramiding = False
                # re self.initialize, then convert the n pyramiding values to downpyramiding
                for j in range(0, maxrange):
                    pyramidingentered = False
                    pyramidingenteredcount = 0
                    for q in range(0, len(botinfopyramiding[j]["data"])):
                        if botinfopyramiding[j]["data"][q]["entered"] == True:
                            pyramidingentered = True
                            pyramidingenteredcount += 1
                    if pyramidingentered and botsettings[j]["pyramiding"] == True and botsettings[j]["currpyramiding"] == True and buyprice < botinfopyramiding[j]["data"][0]["baseprice"] and pyramidingenteredcount > 1:
                        print(" =============== more than one pyramiding entered, buy price < baseprice for that pyramiding bot, then set currpyramiding = False convert n pyramiding to downpyramiding ")
                        highestprice = 0
                        pyramidingcount = 0
                        for q in range(0, len(botinfopyramiding[j]["data"])):
                            if botinfopyramiding[j]["data"][q]["entered"] == True:
                                pyramidingcount = q
                                highestprice = botinfopyramiding[j]["data"][q]["entryprice"]
                        pyramidingcount += 1

                        print(" ========  highestprice   ", highestprice)
                        print(" ===========   pyramidingcount   ", pyramidingcount)

                        self.update.updates(userid, highestprice)

                        self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userid,))
                        botinfo = self.dbcur.fetchall()[0]

                        totalpyramidingentered = 0.0
                        reversedbotinfopyramiding = botinfopyramiding[j]["data"][:pyramidingcount]
                        reversedbotinfopyramiding = reversedbotinfopyramiding[::-1]
                        for l in range(0, len(reversedbotinfopyramiding)):
                            print(" ==========  reversedbotinfopyramiding   ", reversedbotinfopyramiding[l])
                        for q in range(0, pyramidingcount):
                            botinfo[j]["data"][q]["amount"] = reversedbotinfopyramiding[q]["amount"]
                            botinfo[j]["data"][q]["entered"] = True
                            botinfo[j]["data"][q]["entryprice"] = reversedbotinfopyramiding[q]["entryprice"]
                            botinfo[j]["data"][q]["entryamount"] = reversedbotinfopyramiding[q]["entryamount"]
                            if q == 0:
                                botinfo[j]["data"][q]["baseprice"] = reversedbotinfopyramiding[q]["entryprice"]
                            totalpyramidingentered += botinfopyramiding[j]["data"][q]["entryamount"]
                            print(" =============  new botinfo ", botinfo[j]["data"][q])

                        # recalculate how much each remaining of the downpyramiding bot can enter
                        totaldownpyramiding = 0.0
                        for q in range(0, len(botinfo[j]["data"])):
                            totaldownpyramiding += botinfo[j]["data"][q]["entryamount"]
                        totaldownpyramiding -= totalpyramidingentered
                        if len(botinfo[j]["data"]) > pyramidingcount:
                            totaldownpyramiding *= 1.0/float(len(botinfo[j]["data"]) - pyramidingcount)
                        for q in range(pyramidingcount, len(botinfo[j]["data"])):
                            botinfo[j]["data"][q]["entryamount"] = totaldownpyramiding

                        print(" ===========   total downpyramidingg   ", totaldownpyramiding)
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


                # if only one downpyramiding is entered, and buy price > base price for that downpyramiding and currpyramiding = False
                # then 
                for j in range(0, maxrange):
                    downpyramiding = False
                    if botinfo[j]["data"][0]["entered"] == True:
                        downpyramiding = True
                    
                    for q in range(1, len(botinfo[j]["data"])):
                        if botinfo[j]["data"][q]["entered"] == True:
                            downpyramiding = False
                    if downpyramiding and buyprice > botinfo[j]["data"][0]["baseprice"] and botsettings[j]["currpyramiding"] == False:
                        print(" ============   only one downpyramiding is entered but buyprice > baseprice so convert to pyramiding  ")
                        botinfopyramiding[j]["data"][0]["entered"] = True
                        botinfopyramiding[j]["data"][0]["entryprice"] = botinfo[j]["data"][0]["entryprice"]
                        botinfopyramiding[j]["data"][0]["entryamount"] = botinfo[j]["data"][0]["entryamount"]
                        botinfopyramiding[j]["data"][0]["amount"] = botinfo[j]["data"][0]["amount"]

                        botinfo[j]["data"][0]["entered"] = False

                        botsettings[j]["currpyramiding"] = True

                        print(" =====  botinfo   ", botinfo[j]["data"][0])
                        print(" ===== botsettings   ", botsettings[j])
                        print(" ===== botinfopyramiding    ", botinfopyramiding[j]["data"][0])

                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s",(json.dumps(botsettings[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s",(json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps(botinfopyramiding[j]), userid))
                            self.dbconn.commit()

                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s",(json.dumps(botsettings[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s",(json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps(botinfopyramiding[j]), userid))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s",(json.dumps(botsettings[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s",(json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps(botinfopyramiding[j]), userid))
                            self.dbconn.commit()

                        self.dbcur.execute("SELECT botoneinfo, botoneinfopyramiding FROM botsdata WHERE userid = %s", (userid,))
                        temp = self.dbcur.fetchall()[0]
                        print()
                        print(" ======  updated botoneinfo   ", temp[0]["data"][0])
                        print(" =============   updated botoneinfo   ", temp[0]["data"][1])
                        print(" =============   updated botoneinfo   ", temp[0]["data"][2])
                        print(" ===== updated botoneinfopyramiding    ", temp[1]["data"][0])
                        print(" ===== updated botoneinfopyramiding    ", temp[1]["data"][1])
                        print(" ===== updated botoneinfopyramiding    ", temp[1]["data"][2])


                # if only one pyramiding is entered, and buy price < base price for that pyramiding and currpyramiding = True
                # then 
                for j in range(0, maxrange):
                    pyramiding = False
                    if botinfopyramiding[j]["data"][0]["entered"] == True:
                        pyramiding = True
                    for q in range(1, len(botinfopyramiding[j]["data"])):
                        if botinfopyramiding[j]["data"][q]["entered"] == True:
                            pyramiding = False
                    if pyramiding and buyprice < botinfopyramiding[j]["data"][0]["baseprice"] and botsettings[j]["currpyramiding"] == True:
                        print(" ============   only one pyramiding is entered but buyprice < baseprice so convert to downpyramiding  ")
                        botinfo[j]["data"][0]["entered"] = True
                        botinfo[j]["data"][0]["entryprice"] = botinfopyramiding[j]["data"][0]["entryprice"]
                        botinfo[j]["data"][0]["entryamount"] = botinfopyramiding[j]["data"][0]["entryamount"]
                        botinfo[j]["data"][0]["amount"] = botinfopyramiding[j]["data"][0]["amount"]

                        botinfopyramiding[j]["data"][0]["entered"] = False

                        botsettings[j]["currpyramiding"] = False

                        print(" =====  botinfo   ", botinfo[j]["data"][0])
                        print(" ===== botsettings   ", botsettings[j])
                        print(" ===== botinfopyramiding    ", botinfopyramiding[j]["data"][0])

                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s",(json.dumps(botsettings[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s",(json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps(botinfopyramiding[j]), userid))
                            self.dbconn.commit()

                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s",(json.dumps(botsettings[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s",(json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps(botinfopyramiding[j]), userid))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s",(json.dumps(botsettings[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s",(json.dumps(botinfo[j]), userid))
                            self.dbconn.commit()
                            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps(botinfopyramiding[j]), userid))
                            self.dbconn.commit()

                        self.dbcur.execute("SELECT botoneinfo, botoneinfopyramiding FROM botsdata WHERE userid = %s", (userid,))
                        temp = self.dbcur.fetchall()[0]
                        print()
                        print(" ======  updated botoneinfo   ", temp[0]["data"][0])
                        print(" =============   updated botoneinfo   ", temp[0]["data"][1])
                        print(" =============   updated botoneinfo   ", temp[0]["data"][2])
                        print(" ===== updated botoneinfopyramiding    ", temp[1]["data"][0])
                        print(" ===== updated botoneinfopyramiding    ", temp[1]["data"][1])
                        print(" ===== updated botoneinfopyramiding    ", temp[1]["data"][2])

                           
        return "success"



































