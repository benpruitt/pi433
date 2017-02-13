'''
pi433.switch
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

Class-based Etekcity switch abstraction. Handles TCP requests from the
Amazon Echo.
'''
import atexit
from email.utils import formatdate
import logging

from gevent import socket

from .util import getLocalIP, makeSerial
from .rfctrl import sendRFCode
from .pcbctrl import blinkStatusLED


class BaseSwitch(object):

    def _initSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip_addr, self.port))
        sock.listen(5)
        def _closeSock():
            sock.close()
        atexit.register(_closeSock)
        self.sock = sock
        logging.info('Initialized socket for switch "%s" on port "%d"',
                     self.name, self.port)

    def _handle(self, c_sock):
        data = c_sock.recv(1024)
        if data.startswith(b'GET /setup.xml HTTP/1.1'):
            logging.info('Received Echo setup request for '
                         '"%s"' % self.name)
            self._handleSetup(c_sock)
        elif data.startswith(b'POST /upnp/control/basicevent1 HTTP/1.1'):
            logging.info('Received Echo control request for '
                         '"%s"', self.name)
            self._handleRequest(data, c_sock)

    def _handleRequest(self, data, c_sock):
        logging.debug('Received request data: "%s"' % data)
        if b'<BinaryState>0</BinaryState>' in data:
            logging.info('Received Echo off request for "%s"', self.name)
            self.turnOff()
        elif b'<BinaryState>1</BinaryState>' in data:
            logging.info('Received Echo on request for "%s"', self.name)
            self.turnOn()
        date_str = formatdate(timeval=None, localtime=False, usegmt=True)
        # from https://github.com/n8henrie/fauxmo
        response = '\r\n'.join([
                'HTTP/1.1 200 OK',
                'CONTENT-LENGTH: 0',
                'CONTENT-TYPE: text/xml charset="utf-8"',
                'DATE: {}'.format(date_str),
                'EXT:',
                'SERVER: Unspecified, UPnP/1.0, Unspecified',
                'X-User-Agent: Fauxmo',
                'CONNECTION: close']) + 2 * '\r\n'
        c_sock.send(response.encode())
        c_sock.close()

    def _handleSetup(self, c_sock):
        date_str = formatdate(timeval=None, localtime=False, usegmt=True)
        # from https://github.com/n8henrie/fauxmo
        setup_xml = '\r\n'.join([
               '<?xml version="1.0"?>',
               '<root>',
               '<device>',
               '<deviceType>urn:Fauxmo:device:controllee:1</deviceType>',
               '<friendlyName>{}</friendlyName>'.format(self.name),
               '<manufacturer>Belkin International Inc.</manufacturer>',
               '<modelName>Emulated Socket</modelName>',
               '<modelNumber>3.1415</modelNumber>',
               '<UDN>uuid:Socket-1_0-{}</UDN>'.format(self.serial),
               '</device>',
               '</root>']) + 2 * '\r\n'

        # from https://github.com/n8henrie/fauxmo
        setup_response = '\r\n'.join([
               'HTTP/1.1 200 OK',
               'CONTENT-LENGTH: {}'.format(len(setup_xml)),
               'CONTENT-TYPE: text/xml',
               'DATE: {}'.format(date_str),
               'LAST-MODIFIED: Sat, 01 Jan 2000 00:01:15 GMT',
               'SERVER: Unspecified, UPnP/1.0, Unspecified',
               'X-User-Agent: Fauxmo',
               'CONNECTION: close']) + 2 * '\r\n' + setup_xml
        c_sock.send(setup_response.encode())
        c_sock.close()

    def run(self):
        self._initSocket()
        while True:
            c_sock, addr = self.sock.accept()
            self._handle(c_sock)


class EtekcitySwitch(BaseSwitch):

    # Dictionary of `EtekcitySwitch` instances keyed by name
    SWITCHES = {}

    def __init__(self, name, port, on_code, off_code):
        self.name = name
        self.ip_addr = getLocalIP()
        self.serial = makeSerial(name)
        self.port = port
        self.on_code = on_code
        self.off_code = off_code
        EtekcitySwitch.SWITCHES[self.name] = self

    def turnOn(self, blink_led=True):
        sendRFCode(self.on_code)
        logging.info('Turned switch %s on', self.name)
        if blink_led:
            blinkStatusLED()

    def turnOff(self, blink_led=True):
        sendRFCode(self.off_code)
        logging.info('Turned switch %s off', self.name)
        if blink_led:
            blinkStatusLED()


class SwitchGroup(BaseSwitch):

    # Dictionary of `SwitchGroup` instances keyed by name
    GROUPS = {}

    def __init__(self, group_name, group_port, switch_names):
        self.name = group_name
        self.ip_addr = getLocalIP()
        self.serial = makeSerial(group_name)
        self.port = group_port
        try:
            self.switches = [EtekcitySwitch.SWITCHES[s] for s in switch_names]
        except KeyError:
            raise ValueError('Invalid switch name in %s' % repr(switch_names))
        SwitchGroup.GROUPS[self.name] = self

    def turnOn(self, blink_led=True):
        for sw in self.switches:
            sw.turnOn(blink_led=False)
        logging.info('Turned group %s on', self.name)
        if blink_led:
            blinkStatusLED()

    def turnOff(self, blink_led=True):
        for sw in self.switches:
            sw.turnOff(blink_led=False)
        logging.info('Turned group %s off', self.name)
        if blink_led:
            blinkStatusLED()
