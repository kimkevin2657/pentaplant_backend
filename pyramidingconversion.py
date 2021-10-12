
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

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]

            # skips over the user whose first bot range is deactivated
            if botsettings[0]["active"] == False:
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                # if buyprice > baseprice, then currpyramiding = true
                # if buyprice < baseprice, then currpyramiding = false
                #  iff the upper level bot has all been entered
                for j in range(0, len(botinfo)):

                    


                    baseprice = botinfo[j]["data"][0]["baseprice"] 
                    if buyprice > baseprice:
                        botsettings[j]["currpyramiding"] = True
                    if buyprice <= baseprice:
                        botsettings[j]["currpyramiding"] = False




                    if j == 0:
                        self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (botsettings[j], userlist[i][0]))
                        self.dbconn.commit()
                    if j == 1:
                        self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (botsettings[j], userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:
                        self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (botsettings[j], userlist[i][0]))
                        self.dbconn.commit()


        return "success"