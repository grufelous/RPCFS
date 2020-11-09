from xmlrpc.client import ServerProxy

from xmlrpc.server import SimpleXMLRPCServer

import os
import shutil
import sys

from cryptography.fernet import Fernet

from utils.reply import Reply
from utils.config import COORDINATOR_LOCATION


COORDINATOR = ServerProxy(COORDINATOR_LOCATION)

KEY_BS = 0
KEY_BS_SUITE = None


def present_working_directory():
    # print(Reply(success=True, data=os.getcwd()).__str__())
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
    except Exception:
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
    except Exception:
        message = 'Error while reading file'
    return Reply(success=False, message=message)


def test(text):
    print(text)


def register_fs_functions(server):
    server.register_function(list_directory)
    server.register_function(present_working_directory)
    server.register_function(copy_file)
    server.register_function(cat)
    server.register_function(test)


def generate_server_key():
    global KEY_BS
    global KEY_BS_SUITE
    KEY_BS = Fernet.generate_key()
    print(f'Key for server: {KEY_BS}')
    KEY_BS_SUITE = Fernet(KEY_BS)


if __name__ == '__main__':
    fs_port = 7000

    if len(sys.argv) == 2:
        try:
            fs_port = int(sys.argv[1])
        except ValueError:
            print('Supply a valid base port number as an integer')
            exit()

    global server

    max_tries = 10
    fs_port_found = False

    while fs_port_found is False and max_tries:
        try:
            server = SimpleXMLRPCServer(('localhost', fs_port), logRequests=True)
            fs_port_found = True
        except OSError:
            fs_port += 1
        finally:
            max_tries -= 1
    if fs_port_found is False:
        print('Ports already in use. Unable to create an RPC server.')
        exit()

    if os.path.isdir('fs_{}'.format(fs_port)) is False:
        os.mkdir('fs_{}'.format(fs_port))
    os.chdir('fs_{}'.format(fs_port))

    register_fs_functions(server)

    print(COORDINATOR.add_fs(fs_port))

    try:
        print('File server started at port {}'.format(fs_port))
        server.serve_forever()
    except KeyboardInterrupt:
        print(COORDINATOR.remove_fs(fs_port))
        print('File server terminated')
