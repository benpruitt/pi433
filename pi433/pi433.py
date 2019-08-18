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

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver

from .output import EtekcityOutlet
from .pcbctrl import turn12VOn, turnStatusLEDOn
from .webserver import runServer
from .util import byteify, getLocalIP

FORMAT = "[pi433] %(asctime)-15s :: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

NETWORK_INIT_TIMEOUT_M = 5
DEFAULT_CONFIG_FP = os.path.expanduser('~/.pi433/config.json')


def startPi433(config_fp=DEFAULT_CONFIG_FP):
    outlets = []
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
        config_dict = json.load(fh)

    # Init switch objects
    bridge = Bridge(driver, 'pi433 Bridge')
    for outlet_cf in config_dict.get('switches', []):
        outlet = EtekcityOutlet(
            outlet_cf['name'],
            outlet_cf['on_code'],
            outlet_cf['off_code']
        )
        bridge.add_accessory(outlet)
        outlets.append(outlet)

    # Init group objects
    # for group_cf in config_dict.get('groups', []):
    #     groups.append(
    #         SwitchGroup(
    #             group_cf['name'],
    #             group_cf['port'],
    #             group_cf['switches']
    #         )
    #     )
    # Spin up greenlets
    # glts = [spawn(s.run) for s in (switches + groups)]
    # Turn on 12V boost converter and status LED
    turn12VOn()
    turnStatusLEDOn()
    # logging.info('Switch servers started')
    driver = AccessoryDriver(pincode='777-77-777', persist_file='pi433.state')
    driver.add_accessory(accessory=get_bridge(driver))
    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()
    # runWebServer()
    # joinall(glts)
