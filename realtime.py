import websocket
import json
import psycopg2
import json

try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    get_message = json.loads(message.decode('utf-8'))
    if type(get_message['trade_price']) == type(1.0):
        DB_NAME = "pentaplant"
        DB_USER = "pentaplant"
        DB_PASS = "pentaplant_landingpage"
        DB_HOST = "localhost"
        DB_PORT = "5432" 

        conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
        cur = conn.cursor()

        cur.execute("UPDATE realtime SET currentprice = %s WHERE coin = %s AND exchange = %s", (float(get_message["trade_price"]), "bitcoin", "upbit"))
        conn.commit()

        cur.close()
        conn.close()


def on_error(ws, error):
    #print(error)
    ws.on_close(ws)

def on_close(ws):
    print("### closed ###")
    ws.close()

def on_open(ws):
    def run(*args):
        sendData = '[{"ticket":"test"},{"type":"ticker","codes":["USDT-BTC"], "isOnlyRealtime":"true"}]'
        ws.send(sendData)

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    endpoint = "wss://api.upbit.com/websocket/v1"
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(endpoint,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)

    ws.on_open = on_open
    ws.run_forever()