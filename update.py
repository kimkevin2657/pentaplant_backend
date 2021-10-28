
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

class update:
    def __init__(self, dbcur, dbconn):
        self.dbcur = dbcur
        self.dbconn = dbconn

    # takes in userid and price and updates the botsdata and bots
    def updates(self, userid, price):
        self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
        botsettings = self.dbcur.fetchall()[0]

        

        maxrange = 0
        for r in range(0, len(botsettings)):
            if botsettings[r]["active"] == True:
                maxrange = r


        bottomprice = price

        for j in range(0, maxrange):

            totalamount = float(botsettings[j]["amount"])

            entryamount = totalamount*(1.0/float(botsettings[j]["entrynum"]))
            
            dollar_difference = float(price)*(float(botsettings[j]["percentrange"])/100.0)*(1.0/float(botsettings[j]["entrynum"]))


            botsettings[j]["pricediff"] = dollar_difference

            templist = []
            for k in range(0, botsettings[j]["entrynum"]):
                if k == 0:
                    templist.append({"targetprice": bottomprice, "entryprice": bottomprice, "entryamount": entryamount, "entered": False, "baseprice": bottomprice, "amount": 0})
                else:
                    templist.append({"targetprice": bottomprice, "entryprice": bottomprice, "entryamount": entryamount, "entered": False, "amount": 0})
                bottomprice -= dollar_difference


            if j == 0:
                self.dbcur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
                self.dbconn.commit()
                self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[j]), userid))
                self.dbconn.commit()

            if j == 1:
                self.dbcur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
                self.dbconn.commit()
                self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[j]), userid))
                self.dbconn.commit()

            if j == 2:
                self.dbcur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
                self.dbconn.commit()
                self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[j]), userid))
                self.dbconn.commit()

    # takes in userid, price, index of the bots and updates the botsdata and bots
    def updatepyramiding(self, userid, price, index):
        self.dbcur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
        botsettings = self.dbcur.fetchall()[0]

        self.dbcur.execute("SELECT botoneinfo, bottwoinfo, botthreeinfo FROM botsdata WHERE userid = %s", (userid,))
        botinfo = self.dbcur.fetchall()[0]

        if botsettings[index]["active"] == False and botsettings[index]["pyramiding"] == False:
            return "False"

        print(" input  ", price, "   ", userid, "   ", index)
        print()
        bottomprice = price
        totalamount = float(botsettings[index]["amount"])
        entryamount = totalamount*(1.0/float(botsettings[index]["entrynumpyramiding"]))
        totalpercentage = float(botsettings[index]["entrynumpyramiding"])*float(botsettings[index]["percentreturnpyramiding"])
        dollar_difference = (float(price)*(1.0+(totalpercentage/100.0)) - float(price))/float(botsettings[index]["entrynumpyramiding"])

        print(bottomprice,"  ", totalamount, "  ", entryamount, "  ", totalpercentage,"  ", dollar_difference)

        templist = []
        for k in range(0, botsettings[index]["entrynumpyramiding"]):
            if k == 0:
                templist.append({"targetprice": bottomprice, "entryprice": bottomprice, "entryamount": entryamount, "entered": False, "baseprice": price, "amount": 0})
            else:
                templist.append({"targetprice": bottomprice, "entryprice": bottomprice, "entryamount": entryamount, "entered": False, "amount": 0})
            bottomprice += dollar_difference

        if index == 0:
            self.dbcur.execute("UPDATE botsdata SET botoneinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
            self.dbconn.commit()
            self.dbcur.execute("UPDATE bots SET botone = %s WHERE userid = %s", (json.dumps(botsettings[index]), userid))
            self.dbconn.commit()

        if index == 1:
            self.dbcur.execute("UPDATE botsdata SET bottwoinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
            self.dbconn.commit()
            self.dbcur.execute("UPDATE bots SET bottwo = %s WHERE userid = %s", (json.dumps(botsettings[index]), userid))
            self.dbconn.commit()
        if index == 2:
            self.dbcur.execute("UPDATE botsdata SET botthreeinfopyramiding = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
            self.dbconn.commit()
            self.dbcur.execute("UPDATE bots SET botthree = %s WHERE userid = %s", (json.dumps(botsettings[index]), userid))
            self.dbconn.commit()

