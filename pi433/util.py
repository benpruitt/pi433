'''
pi433.util
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

Utility / helper functions

'''
import uuid
from gevent import socket

def byteify(input):
    ''' Recursively encode any `unicode` strings in `str_input` to utf-8
    '''
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def makeSerial(dev_name):
    ''' Generate a deterministic UUID serial number from `dev_name`

    Args:
        dev_name (str): Unique device name

    Derived from https://github.com/n8henrie/fauxmo
    '''

    return str(uuid.uuid3(uuid.NAMESPACE_X500, dev_name))


def getLocalIP():
    ''' Get the local IP address as a string

    Derived from https://github.com/n8henrie/fauxmo
    '''
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    # Workaround for Linux returning localhost
    # See: SO question #166506 by @UnkwnTech
    if ip_address in ['127.0.1.1', '127.0.0.1', 'localhost']:
        tempsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tempsock.connect(('8.8.8.8', 0))
        ip_address = tempsock.getsockname()[0]
        tempsock.close()

    return ip_address