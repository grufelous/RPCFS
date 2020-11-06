from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
from utils.reply import Reply

import os
import shutil
import sys


coordinator_proxy = ServerProxy('http://localhost:3000')

# TODO: This returns "/tmp/fs_<port>"
def present_working_directory():
    return Reply(success=True, data=os.getcwd())

def list_directory():
    return Reply(success=True, data=os.listdir(os.getcwd()))

def copy_file(src, dest):
    if os.path.isfile(src) is False:
        message = 'Error: src file ({}) does not exist'.format(src)
    try:
        shutil.copyfile(src, dest)
        return Reply(success=True, message='Successfully copied')
    except shutil.SameFileError:
        message = 'Error: Can not copy to the same file'
    except IsADirectoryError:
        message = 'Error: Copying folders not allowed'
    except PermissionError:
        message = 'Error: Permission denied'
    except:
        message = 'Error while copying file'
    return Reply(success=False, message=message)

def cat(file_name):
    try:
        f = open(file_name, 'r')
        text = f.read()
        f.close()
        return Reply(success=True, data=text)
    except FileNotFoundError:
        message = 'Error: File does not exist'
    except:
        message = 'Error while reading file'
    return Reply(success=False, message=message)


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
