from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

import os
import shutil
import sys


coordinator_proxy = ServerProxy('http://localhost:3000')

# TODO: This returns "/tmp/fs_<port>"
def present_working_directory():
    return os.getcwd()

def list_directory():
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
        return 'Error while copying file'
    return (src, dest)

def cat(file_name):
    try:
        f = open(file_name, 'r')
        text = f.read()
        f.close()
        return text
    except FileNotFoundError:
        return 'Error: File does not exist'
    except:
        return 'Error while reading file'
    return file_name


if __name__ == '__main__':
    fs_port = 7000
    print(len(sys.argv))
    
    print(sys.argv)
    
    global server
    
    try:
        if len(sys.argv) == 2:
            try:
                fs_port = int(sys.argv[1])
                print(int(sys.argv[1]))
            except ValueError:
                print('Supply a valid port number as an integer')
        server = SimpleXMLRPCServer(('localhost', fs_port), logRequests=True)
    except OSError:
        print('Port {} already in use or unable to create an RPC server on this port'.format(fs_port))
        exit()
        

    if os.path.isdir('/tmp/fs_{}'.format(fs_port)) == False:
        os.mkdir('/tmp/fs_{}'.format(fs_port))
    os.chdir('/tmp/fs_{}'.format(fs_port))
    
    print(coordinator_proxy.add_fs(fs_port))
    
    try:
        print('File server started at port {}'.format(fs_port))
        server.serve_forever()
    except KeyboardInterrupt:
        print(coordinator_proxy.remove_fs(fs_port))
        print('File server terminated')

server.register_function(list_directory)
server.register_function(present_working_directory)
server.register_function(copy_file)
server.register_function(cat)
