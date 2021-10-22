import pyupbit
import psycopg2 # driver 임포트
import json
import time
from pyupbit import Upbit




def realtime_upbit():
    DB_NAME = "pentaplant"
    DB_USER = "pentaplant"
    DB_PASS = "pentaplant_landingpage"
    DB_HOST = "localhost"
    DB_PORT = "5432" 
    dbconn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
    dbcur = dbconn.cursor()

    while(True):

        dbcur.execute("SELECT userid, apikey, secretkey, botactive FROM users")
        users = dbcur.fetchall()

        for i in range(0, len(users)):
            if users[i][1] == None or users[i][2] == None:
                continue

            userid = users[i][0]
            upbit = Upbit(users[i][1], users[i][2])
            balance = ""
            try:
                balance = upbit.get_balances()
            except Exception as ex:
                pass

            if balance == "":
                continue

            btc = 0
            usdt = 0
            krw = 0
            for k in range(0, len(balance)):
                if balance[k]["currency"] == "BTC":
                    btc = balance[k]["balance"]
                if balance[k]["currency"] == "USDT":
                    usdt = balance[k]["balance"]
                if balance[k]["currency"] == "KRW":
                    krw = balance[k]["balance"]
            
            inputjson = json.dumps({"USDT": usdt, "BTC": btc, "KRW": krw})
            dbcur.execute("UPDATE users SET balance = %s WHERE userid = %s", (usdt, userid))
            dbconn.commit()
            dbcur.execute("UPDATE bots SET totalbalance = %s WHERE userid = %s", (inputjson, userid))
            dbconn.commit()

            time.sleep(2)



if __name__ == "__main__":
    realtime_upbit()
