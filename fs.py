from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

import os

server = SimpleXMLRPCServer(('localhost', 3000), logRequests=True)

# proxy = ServerProxy('http://localhost:3000')


def list_directory(dir):
    return os.listdir(dir)

def do_stuff(arg):
    return arg*5
    
server.register_function(list_directory)
server.register_function(do_stuff)

def cli():
    print('fs> ')

if __name__ == '__main__':
    try:
        print("File server started at port ")
        server.serve_forever()
    except KeyboardInterrupt:
        print("File server closed")
    
    

