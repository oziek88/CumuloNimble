from subprocess import Popen
import os
import json

from pyHS100 import SmartPlug, SmartBulb
from pprint import pformat as pf

from flask import Flask, render_template
from flask_sockets import Sockets
from ouimeaux.environment import Environment
import requests
from gevent import pywsgi, sleep, spawn
from geventwebsocket.handler import WebSocketHandler

import pandas as pd

# pyW215 dependencies
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET
import hmac
import time
import logging



_LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
sockets = Sockets(app)
# env = Environment()
# env.start()
# env.discover()
# wemo = env.list_switches()
# print(wemo)
# wemo_switch = env.get_switch(wemo[0])

scenario_1 = pd.read_csv('Scen1.csv', index_col=False).where(pd.notnull, None)
scenario_2 = pd.read_csv('Scen2.csv', index_col=False).where(pd.notnull, None)
scenario_3 = pd.read_csv('Scen3.csv', index_col=False).where(pd.notnull, None)


plug = SmartPlug("172.20.10.8")

@app.route('/')
def home():
    return render_template('index.html')


def send_message(ws, record):
    ws.send(json.dumps(record))

def turn_on(plug):
    plug.turn_on()

def turn_off(plug):
    plug.turn_off()

def turn_fan_off():
    os.system('python2 python2_wemo.py off')

def turn_fan_on():
    os.system('python2 python2_wemo.py off')

def handle_event(event):
    if event == 'turn fan off':
        Popen('python2 python2_wemo.py off'.split())
    elif event == 'turn fan on':
        Popen('python2 python2_wemo.py on'.split())
    elif event == 'turn light on':

    # plug.turn_on()
        spawn(turn_on, plug)
        # requests.put('http://192.168.20.248/api/zK7R5W9GGfgIPv-4DvZzXLRP9MdCj3CTyeNaCN9i/lights/2/state'
        #     , json={"on":True})
    elif event == 'turn light off':
        spawn(turn_off, plug)
        # requests.put('http://192.168.20.248/api/zK7R5W9GGfgIPv-4DvZzXLRP9MdCj3CTyeNaCN9i/lights/2/state'
        #     , json={"on":False})
    else:
        print("Invalid Event " + str(event))


@sockets.route('/websocket')
def websocket(ws):
    state = {
        'websocket': ws,
        'count': 0
    }

    data = scenario_1

    records = data.to_dict('records')

    while not ws.closed:
        count = state['count']

        record = records[count]
        send_message(ws, record)

        event = record['event']
        print('Event: {}'.format(event))
        handle_event(event)

        state['count'] = count + 1
        sleep(.4)


@sockets.route('/websocket2')
def websocket2(ws):
    state = {
        'websocket': ws,
        'count': 0
    }

    data = scenario_2

    event_list = data['event']

    while not ws.closed:
        send_message(state)
        count = state['count']
        event = event_list[count]
        print('Event: {}'.format(event))
        handle_event(event)
        state['count'] = count + 1
        sleep(.5)


@sockets.route('/websocket3')
def websocket3(ws):
    state = {
        'websocket': ws,
        'count': 0
    }

    data = scenario_3

    records = data.to_dict('records')

    while not ws.closed:
        count = state['count']

        record = records[count]
        send_message(ws, record)

        event = record['event']
        print('Event: {}'.format(event))
        handle_event(event)

        state['count'] = count + 1
        sleep(.5)


if __name__ == "__main__":
    handle_event('turn light off')
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

