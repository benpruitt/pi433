'''
pi433.util
(c) Ben Pruitt, 2017 [MIT License, see LICENSE]

Utility / helper functions

'''
import uuid
from gevent import socket


def byteify(str_input):
    ''' Recursively encode any `unicode` strings in `str_input` to utf-8
    '''
    if isinstance(str_input, dict):
        return {byteify(key): byteify(value)
                for key, value in str_input.iteritems()}
    elif isinstance(str_input, list):
        return [byteify(element) for element in str_input]
    elif isinstance(str_input, unicode):
        return str_input.encode('utf-8')
    else:
        return str_input


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
