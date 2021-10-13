

from time import gmtime, strftime
import datetime
import pytz
import time
import json

from pyupbit import Upbit
import pyupbit


def convert_datetime_timezone():
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Seoul")
    dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt



upbit = Upbit("j8wIwxP7cHhAMWkXm8m11g3uEMf2QKf5C19AqpDi", "tZ1KkCe4slf3rxc8FjvHKzrDQGrV6RWzSyfJ1pxd")

print(upbit.get_balance("USDT"))

temp = upbit.get_balance("KRW")
print(temp)

temp = upbit.get_balance("BTC")
print(temp)
#temp - 10000.0

temp = upbit.buy_market_order("KRW-BTC", temp)

print(temp)
#print(json.dumps(upbit.buy_market_order("KRW-BTC", temp),indent=4))

#print()





