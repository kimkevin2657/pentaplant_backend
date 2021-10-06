import pyupbit
import psycopg2 # driver 임포트
import json
import time





def realtime_upbit():
    DB_NAME = "pentaplant"
    DB_USER = "pentaplant"
    DB_PASS = "pentaplant_landingpage"
    DB_HOST = "localhost"
    DB_PORT = "5432" 
    dbconn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
    dbcur = dbconn.cursor()

    while(True):
        temp = pyupbit.get_current_price(["USDT-BTC", "USDT-ETH", "USDT-ADA"])
        BTCprice = float(temp["USDT-BTC"])
        ETHprice = float(temp["USDT-ETH"])
        ADAprice = float(temp["USDT-ADA"])

        dbcur.execute("UPDATE realtime SET currentprice = %s WHERE (coin, exchange) = (%s, %s)",(BTCprice, "BTC/USDT", "Upbit"))
        dbconn.commit()

        dbcur.execute("UPDATE realtime SET currentprice = %s WHERE (coin, exchange) = (%s, %s)",(ETHprice, "ETH/USDT", "Upbit"))
        dbconn.commit()

        dbcur.execute("UPDATE realtime SET currentprice = %s WHERE (coin, exchange) = (%s, %s)",(ADAprice, "ADA/USDT", "Upbit"))
        dbconn.commit()

        temp = pyupbit.get_orderbook(tickers=["USDT-BTC", "USDT-ETH", "USDT-ADA"])
        for i in range(0, len(temp)):
            if temp[i]["market"] == "USDT-BTC":
                askprice = temp[i]["orderbook_units"][0]["ask_price"]
                bidprice = temp[i]["orderbook_units"][0]["bid_price"]
                asksize = temp[i]["orderbook_units"][0]["ask_size"]
                bidsize = temp[i]["orderbook_units"][0]["bid_size"]
                tempjson = json.dumps({"askprice": askprice, "askamount": asksize, "bidprice": bidprice, "bidamount": bidsize})
                dbcur.execute("UPDATE realtime SET orderbook = %s WHERE (coin, exchange) = (%s, %s)", (tempjson, "BTC/USDT", "Upbit"))
                dbconn.commit()
            if temp[i]["market"] == "USDT-ETH":
                askprice = temp[i]["orderbook_units"][0]["ask_price"]
                bidprice = temp[i]["orderbook_units"][0]["bid_price"]
                asksize = temp[i]["orderbook_units"][0]["ask_size"]
                bidsize = temp[i]["orderbook_units"][0]["bid_size"]
                tempjson = json.dumps({"askprice": askprice, "askamount": asksize, "bidprice": bidprice, "bidamount": bidsize})
                dbcur.execute("UPDATE realtime SET orderbook = %s WHERE (coin, exchange) = (%s, %s)", (tempjson, "ETH/USDT", "Upbit"))
                dbconn.commit()
            if temp[i]["market"] == "USDT-ADA":
                askprice = temp[i]["orderbook_units"][0]["ask_price"]
                bidprice = temp[i]["orderbook_units"][0]["bid_price"]
                asksize = temp[i]["orderbook_units"][0]["ask_size"]
                bidsize = temp[i]["orderbook_units"][0]["bid_size"]
                tempjson = json.dumps({"askprice": askprice, "askamount": asksize, "bidprice": bidprice, "bidamount": bidsize})
                dbcur.execute("UPDATE realtime SET orderbook = %s WHERE (coin, exchange) = (%s, %s)", (tempjson, "ADA/USDT", "Upbit"))
                dbconn.commit()

        time.sleep(60)

        break



if __name__ == "__main__":
    realtime_upbit()


