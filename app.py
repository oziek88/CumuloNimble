from flask import Flask, render_template
from flask_sockets import Sockets

from gevent import pywsgi, sleep, spawn
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


def send_message(state):
    ws = state['websocket']
    count = state['count']

    if count % 24 == 0:
        ws.send('ALERT turn off fan')

    ws.send('200')


def receive_message(ws, state):
    message = ws.receive()
    print('Client sent message {}'.format(message))
    spawn(receive_message, ws, state)


@sockets.route('/websocket')
def websocket(ws):
    state = {
        'websocket': ws,
        'count': 0
    }

    spawn(receive_message, ws, state)

    while not ws.closed:
        send_message(state)

        state['count'] = state['count'] + 1
        sleep(1)


if __name__ == "__main__":
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
