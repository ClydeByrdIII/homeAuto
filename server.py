import json
import uuid
import socket
import urllib
import httplib
import sqlite3
import datetime

# input:
#   type: D_COMMAND, command, name
#   type: D_REG, name
#   type: D_NOTIFY, did, name, msg
#   type: D_DELETE, name

# output:
#   type: D_STATUS, status, msg

client_ip_port = 5050

def alert_client(msg):
    conn = httplib.HTTPSConnection('api.pushover.net:443')
    conn.request('POST', '/1/messages.json',
        urllib.urlencode({
        'token': 'aW34oVj5RHAgJ2C7bZC4VPE4haCAUs',
        'user': 'uaFuTcZz62wvmspFi8VMenx24My28Z',
        'message': msg,
    }), { 'Content-type': 'application/x-www-form-urlencoded' })
    conn.getresponse()

def create_status(status, msg):
    return {'type': 'D_STATUS', 'status': status, 'msg': msg}

def send_client_command(ip, command):
    # Connect to the client
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, client_ip_port))

    # Send the data
    dev_data =  {'type': 'D_COMMAND', 'command': command}

    message = json.dumps(dev_data)

    print 'Sending : "%s"' % message
    len_sent = s.send(message)

    if len_sent < 1:
        print 'something went wrong in send_client_command!'

    # Receive a response
    resp = s.recv(1024)
    response = json.loads(resp)

    print 'Received: "%s"' % response
    # Clean up
    s.close()

    return response

# verify Dev_id
def verify_did(conn, did):
    cur = conn.cursor()
    cur.execute("SELECT did FROM devices")
    conn.commit()
        
    row = cur.fetchone()
    cur.close()

    if row == None:
        return False
    return True

# register a device with the server
# return the device id
def register_handle(client_ip, name):
    ret = 'OK'
    ret_msg = str(uuid.uuid4())
    try:
        conn = sqlite3.connect('HAB.db')
        conn.execute('''pragma foreign_keys=ON''')
        conn.execute("INSERT INTO devices VALUES (?,?,?)", (ret_msg, name, client_ip))
        conn.commit()
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()
        ret = 'FAIL'
        ret_msg = repr(e)
        print e
    finally:
        conn.close()
    return create_status(ret, ret_msg)

# notify user of the new event
def notify_handle(data):
    ret = 'OK'
    ret_msg = ''

    try:
        conn=sqlite3.connect('HAB.db')
        conn.execute('''pragma foreign_keys=ON''')
        
        if verify_did(conn, data['did']) == False:
            ret = 'FAIL'
            ret_msg = 'DID Not Found'
        else:
            # checks out; add event
            cur_time = datetime.datetime.now().strftime("%H:%M:%S:%f %m-%d-%Y")
            conn.execute("INSERT INTO events VALUES (?,?,?,?)", (data['did'], data['name'], data['msg'], cur_time))
            conn.commit()
            # alert user
            alert_client(data['name'] + ' says: ' + data['msg']);
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()

        ret = 'FAIL'
        ret_msg = repr(e)
        print e
    finally:
        conn.close()
    return create_status(ret, ret_msg)

def delete_handle(data):
    ret = 'OK'
    ret_msg = ''

    try:
        conn=sqlite3.connect('HAB.db')
        conn.execute('''pragma foreign_keys=ON''')

        # find the device
        cur = conn.cursor()
        cur.execute("SELECT CIP FROM devices WHERE NAME = ?", (data['name'],))
        conn.commit()

        row = cur.fetchone()
        if row == None:
            ret = 'OK'
            ret_msg = data['name'] + ' not found!'
        else:
            print 'Send Delete to Client ' + row[0]
            send_client_command(row[0], 'DELETE')
            # checks out; delete device
            conn.execute("DELETE FROM devices WHERE NAME = ?", (data['name'],))
            conn.commit()
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()

        ret = 'FAIL'
        ret_msg = repr(e)
        print e
    finally:
        cur.close()
        conn.close()
        
    return create_status(ret, ret_msg)

def command_handle(data):
    ret = 'OK'
    ret_msg = ''

    try:
        conn=sqlite3.connect('HAB.db')
        conn.execute('''pragma foreign_keys=ON''')
        
        # find the device
        cur = conn.cursor()
        cur.execute("SELECT CIP FROM devices WHERE NAME = ?", (data['name'],))
        conn.commit()
        
        row = cur.fetchone()
        if row == None:
            ret = 'FAIL'
            ret_msg = data['name'] + ' not found!'
        else:
            print 'Send Data to Client ' + row[0]
            send_client_command(row[0], data['command'])
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()
        ret = 'FAIL'
        ret_msg = repr(e)
        print e
    finally:
        cur.close()
        conn.close()
    
    return create_status(ret, ret_msg)