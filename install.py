#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
pi433 setup

Installs pi433 on a pi zero

Needs to be run with sudo.
'''

import os
import pip
import shutil
import subprocess

try:
    from setuptools import setup, Extension
    from setuptools.command import install_lib, sdist, build_ext
except ImportError:
    from distutils.core import setup, Extension
    from distutils.command import install_lib, sdist, build_ext

LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))
INSTALL_DIR = os.path.expanduser('~/.pi433')


# Check for admin priv
if not os.getuid() == 0:
    raise OSError('Must run setup script with sudo!')

# Create ~/.pi433 directory
if not os.path.isdir(INSTALL_DIR):
    os.makedirs(INSTALL_DIR)

# Copy `pi433` directory to ~/.py433
print('Copying pi433 module...')
module_dir = os.path.join(INSTALL_DIR, 'pi433')
if os.path.isdir(module_dir):
    shutil.rmtree(module_dir)
shutil.copytree(
    os.path.join(LOCAL_DIR, 'pi433'),
    os.path.join(module_dir)
)

# Copy cli.py to ~/.py433
print('Copying "cli.py"...')
shutil.copy(
    os.path.join(LOCAL_DIR, 'cli.py'),
    os.path.join(INSTALL_DIR, 'cli.py')
)

# Copy "config.json" to ~/.py433
print('Copying "config.json"...')
shutil.copy(
    os.path.join(LOCAL_DIR, 'config.json'),
    os.path.join(INSTALL_DIR, 'config.json')
)


# Write pi433 service file
service_txt = '''[Unit]
Description=pi433 service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python %s/cli.py

[Install]
WantedBy=multi-user.target''' % INSTALL_DIR

print('Writing pi433.service...')
SERVICE_PATH = '/lib/systemd/system/' + 'pi433.service'
with open(SERVICE_PATH, 'w') as fh:
    fh.write(service_txt)

print('Setting permissions for pi433.service...')
subprocess.call(
    ['sudo', 'chmod', '644', SERVICE_PATH]
)

print('Restarting systemd...')
subprocess.call(
    ['sudo', 'systemctl', 'daemon-reload']
)

print('Enabling "pi433.service"...')
subprocess.call(
    ['sudo', 'systemctl', 'enable', 'pi433.service']
)

print('Starting "pi433.service"...')
subprocess.call(
    ['sudo', 'systemctl', 'start', 'pi433.service']
)
