import psycopg2 # driver 임포트
import json


userid = 1


DB_NAME = 'pentaplant'
DB_USER = 'pentaplant'
DB_PASS = 'pentaplant_landingpage'
DB_HOST = 'localhost'
DB_PORT = '5432'

conn = psycopg2.connect(host='localhost', dbname=DB_NAME, user=DB_USER, password=DB_PASS, port='5432') # db에 접속
cur = conn.cursor()

cur.execute("SELECT orderbook FROM realtime WHERE (coin, exchange) = (%s, %s)", ("BTC/USDT", "Upbit"))
orderbook = cur.fetchall()[0][0]

buyprice = orderbook["askprice"]
sellprice = orderbook["bidprice"]

cur.execute("SELECT botone, bottwo, botthree FROM bots WHERE userid = %s", (userid,))
temp = cur.fetchall()[0]

for i in range(0, len(temp)):
    if temp[i]["active"] == False:
        continue
    else:

        # botoneinfo = {"data": [ {"targetprice", "entryprice", "entryamount", "entered"} ] }

        templist = []
        for j in range(0, temp[i]["entrynum"]):
            if j == 0:
                templist.append({"targetprice": 0, "entryprice": 0, "entryamount": 0, "entered": False, "baseprice": 0})
            else:
                templist.append({"targetprice": 0, "entryprice": 0, "entryamount": 0, "entered": False})
        
        if i == 0:
            cur.execute("UPDATE botsdata SET botoneinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
            conn.commit()
        if i == 1:
            cur.execute("UPDATE botsdata SET bottwoinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
            conn.commit()
        if i == 2:
            cur.execute("UPDATE botsdata SET botthreeinfo = %s WHERE userid = %s", (json.dumps({"data": templist}), userid))
            conn.commit()

cur.close()
conn.close()