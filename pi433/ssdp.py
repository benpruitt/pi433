'''
pi433.ssdp
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

SSDP server class abstraction to respond to Echo multicasts
'''
import atexit
from email.utils import formatdate
import logging
import struct
import uuid

from gevent import socket


class SSDPServer(object):

    def __init__(self, devices):
        self.devices = devices

    def addDevice(self, device):
        self.devices.append(device)

    def _initSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        # Reuse socket in `TIME_WAIT` state (do not wait for natural timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 1900))
        # 8-byte packed rep of hte multicast group address followed by
        ## the network interface on which to listen
        ## (239.255.255.250 - IPv4 SSDP address)
        ## (INADDR_ANY = any interface)
        mreq = struct.pack("=4sl", socket.inet_aton("239.255.255.250"),
                           socket.INADDR_ANY)
        # Receive packets on the network @ the group address
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        # Close the connection atexit (__del__ GC isn't guaranteed in gevent)
        def _closeSock():
            sock.close()
        atexit.register(_closeSock)
        self.sock = sock

    def _handle(self, data, addr):
        if all(b in data for b in [b'"ssdp:discover"',
                                   b'urn:Belkin:device:**']):
            for device in self.devices:
                name = device.name
                ip_address = device.ip_addr
                port = device.port
                serial = device.serial

                location = 'http://{}:{}/setup.xml'.format(ip_address, port)

                date_str = formatdate(timeval=None, localtime=False,
                                      usegmt=True)
                response = '\r\n'.join([
                        'HTTP/1.1 200 OK',
                        'CACHE-CONTROL: max-age=86400',
                        'DATE: {}'.format(date_str),
                        'EXT:',
                        'LOCATION: {}'.format(location),
                        'OPT: "http://schemas.upnp.org/upnp/1/0/"; ns=01',
                        '01-NLS: {}'.format(uuid.uuid4()),
                        'SERVER: Unspecified, UPnP/1.0, Unspecified',
                        'ST: urn:Belkin:device:**',
                        'USN: uuid:Socket-1_0-{}::urn:Belkin:device:**'
                        .format(serial)]) + 2 * '\r\n'
                self.sock.sendto(response.encode(), addr)

    def run(self):
        self._initSocket()
        while True:
            self._handle(*self.sock.recvfrom(1024))
