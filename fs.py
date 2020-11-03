from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

import os

server = SimpleXMLRPCServer(('localhost', 7000), logRequests=True)

proxy = ServerProxy('http://localhost:3000')

def present_working_directory(dir):
    print("Real physical path: {} ".format(os.getcwd()))
    return os.getcwd()

def list_directory(dir):
    pass

# def copy(src, dest):
#     pass

# def cat(file_name):
#     pass

# def list_directory(dir):
#     return os.listdir(dir)

# def do_stuff(arg):
#     return arg*5

server.register_function(list_directory)
server.register_function(present_working_directory)

def cli():
    print('fs> ')

if __name__ == '__main__':
    try:
        print("File server started at port ")
        server.serve_forever()
    except KeyboardInterrupt:
        print("File server closed")
