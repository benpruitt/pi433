'''
pi433.webserver
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

Lightweight mobile web interface

'''

import logging
from flask import Flask, render_template
from gevent.wsgi import WSGIServer

from .switch import EtekcitySwitch, SwitchGroup
from .util import getLocalIP

class LogWrap(object):

    @staticmethod
    def write(msg):
        logging.info(msg)

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html',
                           switches=EtekcitySwitch.SWITCHES,
                           groups=SwitchGroup.GROUPS)


@app.route('/ts/<esc_switch_name>/<int:state>')
def toggleSwitch(esc_switch_name, state):
    switch_name = esc_switch_name.replace('-', ' ')
    switch_obj = EtekcitySwitch.SWITCHES[switch_name]
    if state == 1:
        switch_obj.turnOn()
    else:
        switch_obj.turnOff()
    return ''


@app.route('/tg/<esc_group_name>/<int:state>')
def toggleGroup(esc_group_name, state):
    group_name = esc_group_name.replace('-', ' ')
    group_obj = SwitchGroup.GROUPS[group_name]
    if state == 1:
        group_obj.turnOn()
    else:
        group_obj.turnOff()
    return ''


def initServer():
    wserver = WSGIServer((getLocalIP(), 80), app,
                         log=LogWrap)
    return wserver