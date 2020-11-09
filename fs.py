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


def copy_file(f1, f2, nonce, payload_ses):
    (ses_key, ses_suite) = extract_ses_key(payload_ses)
    src = ses_suite.decrypt(f'{f1}'.encode()).decode()
    dest = ses_suite.decrypt(f'{f2}'.encode()).decode()
    dec_nonce = ses_suite.decrypt(f'{nonce}'.encode()).decode()
    print(f'src: {src}, dest: {dest}, nonce: {dec_nonce}')
    success = False
    if os.path.isfile(src) is False:
        message = 'Error: src file ({}) does not exist'.format(src)
    try:
        shutil.copyfile(src, dest)
        message = 'Successfully copied'
        success = True
        # return Reply(success=True, message='Successfully copied', nonce=dec_nonce)
    except shutil.SameFileError:
        message = 'Error: Can not copy to the same file'
    except IsADirectoryError:
        message = 'Error: Copying folders not allowed'
    except PermissionError:
        message = 'Error: Permission denied'
    except Exception:
        message = 'Error while copying file'
    message = ses_suite.encrypt(message.encode())
    nonce = ses_suite.encrypt(dec_nonce.encode())
    return Reply(success=success, message=message, nonce=nonce)


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


def extract_ses_key(payload_ses):
    ses_key_recv = payload_ses['key_ab']
    ses_key = KEY_BS_SUITE.decrypt(f'{ses_key_recv}'.encode()).decode()
    print('Kab: ', ses_key)
    return (ses_key, Fernet(ses_key))


def test(payload_arg, payload_ses):
    print(payload_ses)
    # nonce_recv = payload_arg['nonce']
    (ses_key, ses_suite) = extract_ses_key(payload_ses)
    pay_arg_dec = ses_suite.decrypt(f'{payload_arg}'.encode()).decode()
    print(pay_arg_dec)
    test_resp = {
        'pay_arg': pay_arg_dec
    }
    return test_resp


def register_fs_functions(server):
    server.register_function(list_directory)
    server.register_function(present_working_directory)
    server.register_function(copy_file)
    server.register_function(cat)
    server.register_function(test)


def set_server_key(fs_port_offset):
    global KEY_BS
    global KEY_BS_SUITE

    try:
        with open('keys/fs_keys.txt', 'r') as fs_keys:
            for i, line in enumerate(fs_keys):
                if i == fs_port_offset:
                    KEY_BS = line.rstrip().encode()
    except OSError:
        print('Unable to read fs_keys')

    print(f'Key for server: {KEY_BS}')
    KEY_BS_SUITE = Fernet(KEY_BS)
    # enc = KEY_BS_SUITE.encrypt('abc'.encode())
    # dec = KEY_BS_SUITE.decrypt(enc).decode()
    # print(dec)


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

    set_server_key(fs_port % 10)

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
