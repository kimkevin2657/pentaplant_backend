
import random
import numpy as np
import asyncio 
import time
from datetime import datetime as dt
from datetime import date, timedelta
import json
import requests
import psycopg2

class sendtrade:
    def __init__(self, dbcur, dbconn):
        self.dbcur = dbcur
        self.dbconn = dbconn


    def buytrade(self, currentprice, mode="deploy"):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):

            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]


            if botsettings[0]["active"] == False:
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                for j in range(0, len(botinfo)):
                    currlist = botinfo[j]["data"]

                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == False:
                            if currlist[k]["targetprice"] >= currentprice:
                                currlist[k]["entryprice"] = currentprice
                                currlist[k]["entered"] = True

                                # execute trade with the amount currlist[k]["entryamount"]
                                # trade code

                                # insert into transaction database
                                # transaction code

                    if j == 0:
                        self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

                    if j == 1:
                        self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:
                        self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    

        return "success"

    def selltrade(self, currentprice, mode="deploy"):

        self.dbcur.execute("SELECT userid FROM users WHERE botactive = True")
        userlist = self.dbcur.fetchall()

        for i in range(0, len(userlist)):
            
            self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userlist[i][0],))
            botsettings = self.dbcur.fetchall()[0]

            if botsettings[0]["active"] == False:
                continue
            else:
                self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userlist[i][0],))
                botinfo = self.dbcur.fetchall()[0]

                for j in range(0, len(botinfo)):
                    currlist = botinfo[j]["data"]

                    for k in range(0, len(currlist)):
                        if currlist[k]["entered"] == True:
                            if currentprice/currlist[k]["entryprice"] - 1.0 > float(botsettings[j]["percentreturn"])/100.0:
                                currlist[k]["entryprice"] = currentprice
                                currlist[k]["entered"] = True
                                
                                # execute trade with the amount currlist[k]["entryamount"]
                                # trade code

                                # insert into transaction database
                                # transaction code

                    if j == 0:
                        self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

                    if j == 1:
                        self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()
                    if j == 2:
                        self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": currlist}), userlist[i][0]))
                        self.dbconn.commit()

        return "success"


