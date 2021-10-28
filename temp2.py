import requests

"""
tempdict = dict()

tempdict["email"] = "kimkevin2657@naver.com"
tempdict["password"] = "COPPERfield7928!"


r = requests.post("https://api.pentaplant.com:8443/api/user/supportLogin", json=tempdict, verify=False)


success = False
for key,items in r.json().items():
    if key == "userResult":
        if items != None:
            try:
                temp = int(r.json()["userResult"]["userId"])
                success = True
            except Exception as ex:
                print(ex)
                pass
"""

from passlib.hash import sha256_crypt

from pyupbit import Upbit
import pyupbit

import json

temp = Upbit("vEJz0MJY7tmcREx07hIDF9wFS3dkKdW06LeY8bTC", "xYxwyOtUwss4EZsJvtEfLdi6WrxZvf53QgHRgAa2")

usdt = temp.get_balance("USDT")
print(usdt)
btc = temp.get_balance("BTC")
print(btc)

print()


print(json.dumps(temp.get_balances(), indent=4))

"""
print()
user_id = r.json()["userResult"]["userId"]

from requests.auth import HTTPBasicAuth

r = requests.get("https://api.pentaplant.com:8443/api/oauth/token?username="+ str(user_id)+  "&password="+"COPPERfield7928!"+"&grant_type=password", proxies={"http":"15.164.232.119:3030"} ,verify=False)
#r = requests.get('https://api.pentaplant.com:8443/api/oauth/token', auth = HTTPBasicAuth(user_id, "COPPERfield7928!"), verify=False)


print(r.json())

return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

"""





