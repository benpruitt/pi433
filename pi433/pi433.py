'''
pi433.pi433
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

Main entry point for pi433

'''
import logging
import json
import os
import sys
import time

from gevent import spawn, joinall, sleep

from .switch import EtekcitySwitch, SwitchGroup
from .pcbctrl import turn12VOn, turnStatusLEDOn
from .webserver import initServer
from .util import byteify, getLocalIP

FORMAT = "[pi433] %(asctime)-15s :: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

NETWORK_INIT_TIMEOUT_M = 5
DEFAULT_CONFIG_FP = os.path.expanduser('~/.pi433/config.json')


def startPi433(config_fp=DEFAULT_CONFIG_FP):
    switches = []
    groups = []

    # Wait for the network to come up
    t1 = time.time()
    while True:
        if time.time() - t1 > (NETWORK_INIT_TIMEOUT_M * 60):
            logging.warning('Timeout waiting for device network to come up')
            sys.exit(1)
        try:
            getLocalIP()
            break
        except:
            sleep(5)

    # Load config file from fp
    with open(config_fp) as fh:
        config_dict = byteify(json.load(fh))

    # Init switch objects
    for switch_cf in config_dict.get('switches', []):
        switches.append(
            EtekcitySwitch(
                switch_cf['name'],
                switch_cf['port'],
                switch_cf['on_code'],
                switch_cf['off_code']
            )
        )

    # Init group objects
    for group_cf in config_dict.get('groups', []):
        groups.append(
            SwitchGroup(
                group_cf['name'],
                group_cf['port'],
                group_cf['switches']
            )
        )
    # Init webserver
    webserver = initServer()
    # Spin up greenlets
    glts = [spawn(s.run) for s in (switches + groups)]
    # Turn on 12V boost converter and status LED
    turn12VOn()
    turnStatusLEDOn()
    logging.info('Switch servers started')
    webserver.serve_forever()
    joinall(glts)
