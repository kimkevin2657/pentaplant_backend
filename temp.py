

from time import gmtime, strftime
import datetime
import pytz
import time
import json

from pyupbit import Upbit
import pyupbit
import psycopg2


def convert_datetime_timezone():
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Seoul")
    dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt



DB_NAME = 'pentaplant'
DB_USER = 'pentaplant'
DB_PASS = 'pentaplant_landingpage'
DB_HOST = 'localhost'
DB_PORT = '5432'



conn = psycopg2.connect(host='localhost', dbname=DB_NAME, user=DB_USER, password=DB_PASS, port='5432') # db에 접속
cur = conn.cursor()

cur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (1,))
temp = cur.fetchall()[0]

upbit = Upbit(temp[0], temp[1])

print(upbit.get_balance("KRW"))
print(upbit.get_balance("USDT"))
print(upbit.get_balance("BTC"))



"""
upbit = Upbit("vEJz0MJY7tmcREx07hIDF9wFS3dkKdW06LeY8bTC", "xYxwyOtUwss4EZsJvtEfLdi6WrxZvf53QgHRgAa2")

print(upbit.get_balance("USDT"))

krw = upbit.get_balance("KRW")
print(krw)
krw2 = krw*(1.0 - 0.0025)
inputkrw = int(krw2)
print(krw)

temp = upbit.get_balance("BTC")
print(temp)
#temp - 10000.0
"""


"""
temp = upbit.buy_market_order("KRW-BTC", inputkrw)

print(temp)
"""

#print(json.dumps(upbit.buy_market_order("KRW-BTC", temp),indent=4))

#print()





