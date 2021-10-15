
import random
import numpy as np
import asyncio 
import time
from datetime import datetime as dt
from datetime import date, timedelta
import json
import requests
import psycopg2

class pyramidingconversion:
    def __init__(self, dbcur, dbconn):
        self.dbcur = dbcur
        self.dbconn = dbconn


    def update(self, buyprice, sellprice):

        #print(" ======  pyramidingconversion ")

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            #print(" === user ", i)

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]
            #print(" === botsettings ", json.dumps(botsettings[0], indent=4))
            #print(" === botsettings ", json.dumps(botsettings[1], indent=4))
            #print(" === botsettings ", json.dumps(botsettings[2], indent=4))

            self.dbcur.execute("SELECT firsttrading FROM bots WHERE userid = %s", (userlist[i][0],))
            firsttrading = self.dbcur.fetchall()[0][0]
            if firsttrading:
                continue

            # skips over the user whose first bot range is deactivated
            if botsettings[0]["active"] == False:
                #print(" === skipping over this user since all bots inactive ")
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]
                #print(" === botinfo ", json.dumps(botinfo[0],indent=4))
                #print(" === botinfo ", json.dumps(botinfo[1],indent=4))
                #print(" === botinfo ", json.dumps(botinfo[2],indent=4))

                # if buyprice > baseprice, then currpyramiding = true
                # if buyprice < baseprice, then currpyramiding = false
                #  iff the upper level bot has all been entered

                maxrange = 0
                for r in range(0, len(botinfo)):
                    if botinfo[r] == None:
                        maxrange = r
                        break
                    else:
                        maxrange = r

                print(" maxrange at pyramidingconversion  ", maxrange)

                #for j in range(0, len(botinfo)):
                for j in range(0, maxrange):
                    #print(" === botinfo index ", j)

                    if j == 0:

                        tempbool = True
                        #for k in range(0, len(botinfo)):
                        for k in range(0, maxrange):
                            for l in range(0, len(botinfo[k]["data"])):
                                if botinfo[k]["data"][l]["entered"] == True:
                                    tempbool = False

                        #print(" === botindex 0 ", " tempbool ", tempbool)
                        if tempbool:

                            baseprice = float(botinfo[j]["data"][0]["baseprice"])
                            #print(" === botindex 0 ", baseprice, "   ", buyprice, "   ", type(baseprice))
                            if buyprice > baseprice:
                                #print(" === botindex 0 buyprice is greater than baseprice")
                                botsettings[j]["currpyramiding"] = True
                            else:
                                botsettings[j]["currpyramiding"] = False

                        #print(" === botindex 0 botsettings  ",json.dumps(botsettings[j],indent=4))

                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                            self.dbconn.commit()

                    else:

                        tempbool = True
                        for k in range(0, j):
                            for l in range(0, len(botinfo[k]["data"])):
                                if botinfo[k]["data"][l]["entered"] == False:
                                    tempbool = False


                        #print(" === botindex ", j, " tempbool ", tempbool)
                        if tempbool:
                            #print(" === botindex ",j, " ", baseprice, "   ", buyprice)
                            baseprice = float(botinfo[j]["data"][0]["baseprice"]) 
                            if buyprice > baseprice:
                                botsettings[j]["currpyramiding"] = True
                            else:
                                botsettings[j]["currpyramiding"] = False
                                
                        #print(" === botindex ",j," botsettings  ",json.dumps(botsettings[j],indent=4))
                        if j == 0:
                            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 1:
                            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                            self.dbconn.commit()
                        if j == 2:
                            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]), userlist[i][0]))
                            self.dbconn.commit()



        return "success"