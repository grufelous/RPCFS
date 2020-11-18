from xmlrpc.server import SimpleXMLRPCServer

from utils.config import LOCALHOST, COORDINATOR_PORT
from utils.fernet_helper import encode_data, decode_data

from cryptography.fernet import Fernet

SERVER = SimpleXMLRPCServer((LOCALHOST, COORDINATOR_PORT), logRequests=True)
FILESERVERS = list()

FS_KEYS = list()
CLIENT_KEYS = list()


def add_fs(fs_port):
    if fs_port in FILESERVERS:
        return f'Port {fs_port} occupied'
    FILESERVERS.append(fs_port)
    print('Active fs: ', FILESERVERS)
    return f'Started fs at port {fs_port}'


def remove_fs(fs_port):
    if fs_port not in FILESERVERS:
        return f'Port {fs_port} already removed'
    FILESERVERS.remove(fs_port)
    print('Active fs: ', FILESERVERS)
    return f'Closed fs at port {fs_port}'


def get_fs():
    return FILESERVERS


def get_enc_session_key(offset_a, port_b, nonce):
    key_ab = Fernet.generate_key()
    print(f'Generating session key for client {offset_a} and fs {port_b}')
    print(f'Kab: {key_ab}')
    key_as = CLIENT_KEYS[offset_a % 10]
    key_bs = FS_KEYS[port_b % 10]
    key_as_suite = Fernet(key_as)
    key_bs_suite = Fernet(key_bs)
    for_a = {
        'port_b': key_as_suite.encrypt(encode_data(port_b)),
        'key_ab': key_as_suite.encrypt(key_ab),
        'nonce': key_as_suite.encrypt(encode_data(nonce)),
    }
    for_b = {
        'client_id': key_bs_suite.encrypt(encode_data(offset_a)),
        'key_ab': key_bs_suite.encrypt(key_ab)
    }
    resp = {
        'for_a': for_a,
        'for_b': for_b
    }
    return resp


def read_keys():
    global FS_KEYS
    global CLIENT_KEYS

    try:
        with open('keys/fs_keys.txt', 'r') as fs_keys:
            for i, line in enumerate(fs_keys):
                FS_KEYS.append(line.rstrip().encode())
    except OSError:
        print('Coordinator unable to read fs_keys')
        raise

    try:
        with open('keys/client_keys.txt', 'r') as client_keys:
            for i, line in enumerate(client_keys):
                CLIENT_KEYS.append(line.rstrip().encode())
    except OSError:
        print('Coordinator unable to read client_keys')
        raise


if __name__ == '__main__':
    SERVER.register_function(add_fs)
    SERVER.register_function(remove_fs)
    SERVER.register_function(get_fs)
    SERVER.register_function(get_enc_session_key)

    try:
        read_keys()
    except OSError:
        print('Coordinator unable to read one or more of fs_keys or client_keys. Exiting...')
        exit()

    try:
        print(f'Central coordinator started at port {COORDINATOR_PORT}')
        SERVER.serve_forever()
    except KeyboardInterrupt:
        print('Coordinator terminated')
