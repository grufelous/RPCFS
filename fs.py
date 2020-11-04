from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

import os

fs_port = 7000

server = SimpleXMLRPCServer(('localhost', fs_port), logRequests=True)

proxy = ServerProxy('http://localhost:3000')

def present_working_directory(dir):
    print('Real physical path: {} '.format(os.getcwd()))
    return os.getcwd()

def list_directory(dir):
    return os.listdir(dir)

def copy_file(src, dest):
    pass

def cat(file_name):
    pass

server.register_function(list_directory)
server.register_function(present_working_directory)
server.register_function(copy_file)
server.register_function(cat)

def cli():
    print('fs> ')

if __name__ == '__main__':
    try:
        print('File server started at port {}'.format(fs_port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('File server terminated')
