



class upbitapi:

    def __init__(self):
        self.temp = 1


    def total_balance(self, userid, cur):
        from pyupbit import Upbit
        import pyupbit
        cur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userid,))
        temp = cur.fetchall()[0]

        krw = 0
        usdt = 0
        btc = 0
        try:
            upbit = Upbit(temp[0], temp[1])
            krw = upbit.get_balance("KRW")
            usdt = upbit.get_balance("USDT")
            btc = upbit.get_balance("BTC")
        except Exception as ex:
            print(ex)

        return krw, usdt, btc

    def usdt_balance(self, userid, cur):
        from pyupbit import Upbit
        import pyupbit
        cur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userid,))
        temp = cur.fetchall()[0]

        usdt = 0
        try:
            upbit = Upbit(temp[0], temp[1])
            usdt = upbit.get_balance("USDT")
        except Exception as ex:
            print(ex)

        return usdt       
    

    def buy_usdt(self, userid, cur):
        from pyupbit import Upbit
        import pyupbit
        import time
        cur.execute("SELECT apikey, secretkey FROM users WHERE userid = %s", (userid,))
        temp = cur.fetchall()[0]

        krw = 0
        try:
            upbit = Upbit(temp[0], temp[1])
            krw = upbit.get_balance("KRW")
        except Exception as ex:
            print(ex)
        krw2 = int("{:.0f}".format(krw*(1.0 - 0.0025)))
        try:
            temp = upbit.buy_market_order("KRW-BTC", krw2)
        except Exception as ex:
            print(ex)
        time.sleep(1)
        btc = 0
        try:
            btc = upbit.get_balance("BTC")
        except Exception as ex:
            print(ex)
        btc = float("{:.4f}".format(btc*(1.0 - 0.0025)))
        try:
            temp = upbit.sell_market_order("USDT-BTC", btc)
        except Exception as ex:
            print(ex)
        time.sleep(1)
        usdt = 0
        try:
            usdt = upbit.get_balance("USDT")
        except Exception as ex:
            print(ex)


        return usdt