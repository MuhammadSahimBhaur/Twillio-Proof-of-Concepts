### code originally from documentation; https://github.com/twilio/media-streams/blob/master/python/basic/server.py
from flask import Flask, render_template, Response
from flask_sock import Sock

from gevent import monkey
monkey.patch_all()

import json
import base64
import ffmpeg


HTTP_SERVER_PORT = 8080
LOGGING = True

app = Flask(__name__)
sock = Sock(app)

@app.route("/", methods=["GET"])
def isRootLive():
    log("isRootLive") 
    return "OK", 200


@app.route("/root", methods=["POST", "GET"])
def startStreamRecording():
    log("startStreamRecording")
    return sendXMLTemplate()

@sock.route("/recordstream")
def recordStream(ws):
    log("WS connected /media1")
    count = 0
    while True:
        msg = ws.receive()
        if msg is None:
            log("Connection closed. Total messages:{}".format(count))
            break
        handleMsg(msg)
        count+=1

# Helper Functions #

def sendXMLTemplate():
    try:
        xml = render_template('streams.xml')
        return Response(xml, mimetype="text/xml")
    except:
        print("error")

def log(msg, *args):
    if(LOGGING):
        print(f"log: ", msg, *args, flush=True)

def handleMsg(msg):
    msgData = json.loads(msg)

    if msgData.get("event") == "media":
        msgDataPayload = msgData["media"]["payload"]
        appendPayloadToFile(msgDataPayload)

def appendPayloadToFile(payload):
    raw = base64.b64decode(payload)

    with open("output.mulaw", "ab") as f:
        f.write(raw)


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()
