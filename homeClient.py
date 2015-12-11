#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import json
from client import *

ip = '127.0.0.1'
name = 'mac'

did_rec = False
did = ''

while did_rec == False:

  did = register_client(ip, name)
  if did != '':
    did_rec = True
    print did

notify_client(ip, did, name, 'DEEZ NUTZ!')

notify_client(ip, did, name, 'Got EM!')

