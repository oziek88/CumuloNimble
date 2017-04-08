import time

from flask import Flask, render_template
from flask_sockets import Sockets

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler


app = Flask(__name__)
sockets = Sockets(app)


@app.route('/')
def home():
    return render_template('index.html')


@sockets.route('/echo')
def echo_socket(ws):
      while not ws.closed:
          message = ws.receive()
          ws.send(message)


@sockets.route('/websocket')
def websocket(ws):
    count = 0
    while not ws.closed:
        ws.send('200')
        if count % 24 == 0:
            ws.send('ALERT turn off fan')

        count += 1
        time.sleep(1)


if __name__ == "__main__":
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
