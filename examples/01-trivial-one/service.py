#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import signal
import configparser
import hashlib
import argparse
import json

CONFIGURATION_DIGEST = None
CONFIGURATION = None

def load_configuration(path):
    global CONFIGURATION_DIGEST, CONFIGURATION
    new_digest = file_digest(path)
    if new_digest == CONFIGURATION_DIGEST:
        print('Configuration reload not required - same content ({})'.format(new_digest))
        return
    CONFIGURATION = ini_parser(path)
    print('New Configuration')
    print(json.dumps(CONFIGURATION, indent=4)) # json fpr pretty printing
    CONFIGURATION_DIGEST = new_digest

def ini_parser(path):
    parser = configparser.ConfigParser()
    parser.read(path)
    d = dict()
    for key in parser['DEFAULT']:
        d[key] = parser['DEFAULT'][key]
    for section in parser.sections():
        for key in parser[section]:
            d[key] = parser[section][key]
    return d

def handler_sighup(signum, frame):
    print('SIGHUP received, reload configuration now')
    load_configuration(args.configuration)
    return True

def file_digest(path):
    return hashlib.md5(open(path,'rb').read()).hexdigest()

signal.signal(signal.SIGHUP, handler_sighup)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configuration", required=True)
args = parser.parse_args()

print('Service read configuration')
load_configuration(args.configuration)

print('Service starting now')
print('call "kill -s HUP {}" to enforce configuration reload'.format(os.getpid()))
while True:
    time.sleep(1)


