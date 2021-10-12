import psycopg2 # driver 임포트
import json





DB_NAME = 'pentaplant'
DB_USER = 'pentaplant'
DB_PASS = 'pentaplant_landingpage'
DB_HOST = 'localhost'
DB_PORT = '5432'





conn = psycopg2.connect(host='localhost', dbname=DB_NAME, user=DB_USER, password=DB_PASS, port='5432') # db에 접속
cur = conn.cursor()

cur.execute("ALTER TABLE botsdata ADD COLUMN botoneinfopyramiding JSONB")
conn.commit()

cur.execute("ALTER TABLE botsdata ADD COLUMN bottwoinfopyramiding JSONB")
conn.commit()

cur.execute("ALTER TABLE botsdata ADD COLUMN botthreeinfopyramiding JSONB")
conn.commit()

"""
cur.execute("ALTER TABLE transaction ADD COLUMN entrytime VARCHAR(256)")
conn.commit()

cur.execute("ALTER TABLE transaction ADD COLUMN baseamount DOUBLE PRECISION")
conn.commit()
"""

cur.close()

conn.close()



"""
cur.execute("ALTER TABLE users ADD COLUMN botactive BOOLEAN")
conn.commit()
"""


"""
templist = []
for i in range(0, 10):
    templist.append({"targetprice": 0, "entryprice": 0, "entryamount": 0, "entered": False})

tuple1 = json.dumps({"data": templist})

templist = []
for i in range(0, 10):
    templist.append({"targetprice": 0, "entryprice": 0, "entryamount": 0, "entered": False})
tuple2 = json.dumps({"data": templist})


tuple3 = json.dumps({"data": [{"targetprice": 0, "entryprice": 0, "entryamount": 0, "entered": False}]})

cur.execute("INSERT INTO botsdata (userid, botoneinfo, bottwoinfo, botthreeinfo) VALUES (%s, %s, %s, %s)",(1, tuple1, tuple2, tuple3))
conn.commit()
"""



















