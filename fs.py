from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

import os

import shutil

fs_port = 7000

server = SimpleXMLRPCServer(('localhost', fs_port), logRequests=True)

proxy = ServerProxy('http://localhost:3000')

def present_working_directory():
    return os.getcwd()

def list_directory(dir):
    return os.listdir(os.getcwd())

def copy_file(src, dest):
    if os.path.isfile(src) is False:
        return 'Error: src file ({}) does not exist'.format(src)
    try:
        shutil.copyfile(src, dest)
        return 'Successfully copied'
    except shutil.SameFileError:
        return 'Error: Can not copy to the same file'
    except IsADirectoryError:
        return 'Error: Copying folders not allowed'
    except PermissionError:
        return 'Error: Permission denied'
    except:
        return 'Error'
    return (src, dest)

def cat(file_name):
    return file_name

server.register_function(list_directory)
server.register_function(present_working_directory)
server.register_function(copy_file)
server.register_function(cat)

def cli():
    print('fs> ')

if __name__ == '__main__':
    if os.path.isdir('fs_{}'.format(fs_port)) == False:
        os.mkdir('fs_{}'.format(fs_port))
    os.chdir('fs_{}'.format(fs_port))
    try:
        print('File server started at port {}'.format(fs_port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('File server terminated')
