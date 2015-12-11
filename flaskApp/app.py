from flask import Flask, render_template, request
import sqlite3
import socket
import json

db_filename = '../HAB.db'
my_ip = ''

app = Flask(__name__)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def delete_event(did, t):
    try:
        conn=sqlite3.connect(db_filename)
        conn.execute('''pragma foreign_keys=ON''')

        conn.execute("DELETE FROM events WHERE DID = ? AND TIME = ?", (did, t))
        conn.commit()
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()
        print e
    finally:
        conn.close()

def send_command(name, command):
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((my_ip, 8080))

    if command == 'DELETE':
        dev_data = {'type': 'D_DELETE', 'name': name}
    else:
        dev_data =  {'type': 'D_COMMAND', 'name': name, 'command': command}

    message = json.dumps(dev_data)
    print 'Sending : "%s"' % message
    len_sent = s.send(message)

    # Receive a response
    resp = s.recv(1024)
    print 'Received: "%s"' % resp

    # Clean up
    s.close()

@app.route('/')
def main():
    try:
        conn = sqlite3.connect(db_filename)
        conn.execute('''pragma foreign_keys=ON''')
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        rows = cur.fetchall()
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()
        print e
    finally:
        conn.close()

    return render_template('index.html', rows=rows)

@app.route('/delete', methods=['POST'])
def delete():

    if request.method == 'POST':
        delete_event(request.form['did'], request.form['time'])
    try:
        conn = sqlite3.connect(db_filename)
        conn.execute('''pragma foreign_keys=ON''')
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        rows = cur.fetchall()
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()
        print e
    finally:
        conn.close()
    return render_template('index.html', rows=rows)

@app.route('/command', methods=['POST'])
def command():

    if request.method == 'POST':
        if request.form['name'] != '' and request.form['command'] != '':
            send_command(request.form['name'], request.form['command'])

    try:
        conn = sqlite3.connect(db_filename)
        conn.execute('''pragma foreign_keys=ON''')
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        rows = cur.fetchall()
    except Exception as e:
        # Roll back any change if something goes wrong
        conn.rollback()
        print e
    finally:
        conn.close()
    return render_template('index.html', rows=rows)

if __name__ == '__main__':
    my_ip = get_ip_address()
    app.run(host='0.0.0.0')