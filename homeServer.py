import json
import threading
import SocketServer
from server import *


class ThreadedDeviceRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        
        dev_data = self.request.recv(1024)
        data = json.loads(dev_data);

        print self.request.getpeername()

        if data['type'] == 'D_REG':
          response = register_handle(self.request.getpeername()[0], data['name'])
        elif data['type'] == 'D_NOTIFY':
          response = notify_handle(data)
        elif data['type'] == 'D_DELETE':
          response = delete_handle(data)
        elif data['type'] == 'D_COMMAND':
          response = command_handle(data, 'DELETE')
        else:
          response = create_status('FAIL', 'type "' + data['type'] + '" was not found')

        message = json.dumps(response)
        
        print '%s : %s' % ('Response is ', message)
        self.request.send(message)
        return

class ThreadedDeviceServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':
    import socket
    import threading

    address = ('localhost', 8080) # let the kernel give us a port
    server = ThreadedDeviceServer(address, ThreadedDeviceRequestHandler)
    server.allow_reuse_address = True

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()
    print 'Server loop running in thread:', t.getName()
    
    # Don't exit
    while True:
      pass