import json
import uuid
import socket
import sqlite3
import os

server_ip_port = 8080;
did_filename = 'did.data'
# return did
def register_client(ip, name):
    did = ''

    # is there already a did
    if os.path.isfile(did_filename) == True:
        f = open(did_filename, 'rb')
        did = f.readline()
    else:
        # Connect to the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, server_ip_port))


        # Send the data
        dev_data =  {'type': 'D_REG', 'name': name}

        message = json.dumps(dev_data)
        print 'Sending : "%s"' % message
        len_sent = s.send(message)

        # Receive a response
        resp = s.recv(1024)
        print 'Received: "%s"' % resp

        response = json.loads(resp)
        # Clean up
        s.close()

        if response['type'] == 'D_STATUS':
            if response['status'] == 'OK':
                did = response['msg']
                f = open(did_filename, 'wb')
                f.write(did)
    return did


def notify_client(ip, did, name, msg):

    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, server_ip_port))

    # Send the data
    dev_data =  {'type': 'D_NOTIFY', 'did': did, 'name': name, 'msg': msg}

    message = json.dumps(dev_data)
    print 'Sending : "%s"' % message
    len_sent = s.send(message)

    # Receive a response
    resp = s.recv(1024)
    print 'Received: "%s"' % resp

    response = json.loads(resp)
    # Clean up
    s.close()

    return response

def delete_command():
    os.remove(did_filename)
