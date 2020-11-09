import re
from pathlib import Path

import sys

from xmlrpc.client import ServerProxy

from cryptography.fernet import Fernet

from utils.reply import Reply
from utils.config import URI, COORDINATOR_LOCATION


COORDINATOR = ServerProxy(COORDINATOR_LOCATION)
FILESERVERS = list()
ACTIVE_FILESERVER = None
ROOT = Path('/')
ACTIVE_DIRECTORY = ROOT
ACTIVE_PORT = 0

KEY_AS = 0
KEY_AS_SUITE = None
OFFSET_A = 0

supported_commands = {
    'pwd': 0,
    'ls': 0,
    'cp': 2,
    'cat': 1,
    'help': 0,
    'cd': 1,
    'exit': 0,
    'test': 1,
}


def help_message():
    print('Supported commands: ')
    print('\tpwd')
    print('\tls')
    print('\tcp <source_file> <destination_file>')
    print('\tcat <file>')
    print('\thelp')
    print('\tcd')
    print('\texit')
    print('Use full paths as needed')


def print_list(data_list: list):
    for element in data_list:
        print(element)


def pwd():
    return str(ACTIVE_DIRECTORY)


def get_friendly_name(port: int):
    if port is None:
        return None
    return f'fs_{port}'


def get_port_from_friendly_name(name: str) -> int:
    try:
        port = int(re.findall(r'\d+', name)[0])
        return port
    except IndexError:
        return None


def change_active_fileserver(dir: str):
    global FILESERVERS
    global ACTIVE_FILESERVER
    global ACTIVE_DIRECTORY
    global ACTIVE_PORT
    path = Path(dir)
    if ACTIVE_FILESERVER is not None and path == Path('..'):
        ACTIVE_FILESERVER = None
        ACTIVE_DIRECTORY = ROOT
        ACTIVE_PORT = 0
    else:
        port = get_port_from_friendly_name(str(path))
        if port in FILESERVERS:
            ACTIVE_FILESERVER = ServerProxy(f'{URI}:{port}')
            ACTIVE_DIRECTORY = Path(get_friendly_name(port))
            ACTIVE_PORT = port
    print('Active port: ', ACTIVE_PORT)


def is_mount_point_root() -> bool:
    global ACTIVE_DIRECTORY
    return ACTIVE_DIRECTORY == ROOT


def update_fileservers():
    global FILESERVERS
    FILESERVERS = COORDINATOR.get_fs()


def get_session_key(nonce=42):
    global OFFSET_A
    global ACTIVE_PORT
    if ACTIVE_PORT == 0:
        print('No active server')
        return
    ses = COORDINATOR.get_enc_session_key(OFFSET_A, ACTIVE_PORT, nonce)
    ses = dict(ses)
    for_client = ses['for_a']
    port_b_recv = for_client['port_b']
    ses_key_recv = for_client['key_ab']
    nonce_recv = for_client['nonce']
    # print('PB: ', port_b_recv)
    # print('Ses: ', ses_key_recv)

    ses_key = KEY_AS_SUITE.decrypt(f'{ses_key_recv}'.encode()).decode()
    port_b = KEY_AS_SUITE.decrypt(f'{port_b_recv}'.encode()).decode()
    nonce_dec = KEY_AS_SUITE.decrypt(f'{nonce_recv}'.encode()).decode()
    print(port_b)
    print(type(port_b))
    print(f'Nonce dec: {nonce_dec}')
    try:
        port_b = int(port_b)
    except TypeError:
        print('Port is NaN')
    finally:
        if(port_b != ACTIVE_PORT):
            print('Active port changed or imposter detected')
            # return (None, None)
            exit()
    print(f'PBR: {port_b}')
    print(f'Kab: {ses_key}')
    # port_b = KEY_AS_SUITE.decrypt(for_client['port_b'])
    # print(f'Received port b: {port_b}')
    for_fs = ses['for_b']
    print(ses)
    return (ses_key, for_fs)


def cli():
    str_inp = input('client> ')
    tokens = ' '.join(str_inp.split(' ')).split()

    if len(tokens) == 0:
        print('Empty input')
    else:
        cmd = tokens[0]
        num_tokens = len(tokens) - 1
        if cmd not in supported_commands:
            print('Command not found')
        elif num_tokens != supported_commands[cmd]:
            print('Syntax error: argument mismatch')
        else:
            if cmd == 'help':
                help_message()
            elif cmd == 'pwd':
                print(pwd())
            elif cmd == 'ls':
                if is_mount_point_root():
                    update_fileservers()
                    print_list(map(get_friendly_name, FILESERVERS))
                else:
                    print_list(ACTIVE_FILESERVER.list_directory()['data'])
            elif cmd == 'cp' and ACTIVE_FILESERVER:
                print(ACTIVE_FILESERVER.copy_file(tokens[1], tokens[2])['message'])
            elif cmd == 'cat' and ACTIVE_FILESERVER:
                cat_reply = dict(ACTIVE_FILESERVER.cat(tokens[1]))
                if cat_reply['success'] is True:
                    print(cat_reply['data'])
                else:
                    print(cat_reply['message'])
            elif cmd == 'cd':
                change_active_fileserver(tokens[1])
            elif cmd == 'exit':
                exit()
            elif cmd == 'test':
                (ses_key, enc_ses_key) = get_session_key()
                print('S: ', ses_key)
                ses_suite = Fernet(ses_key)
                payload_arg = ses_suite.encrypt(tokens[1].encode())
                # payload_nonce = ses_suite.encrypt(enc_ses_key)
                recv_dict = ACTIVE_FILESERVER.test(payload_arg, enc_ses_key)
                print(recv_dict)


def set_client_key(client_offset):
    global KEY_AS
    global KEY_AS_SUITE
    global OFFSET_A
    OFFSET_A = client_offset

    try:
        with open('keys/client_keys.txt', 'r') as client_keys:
            for i, line in enumerate(client_keys):
                if i == client_offset:
                    KEY_AS = line.rstrip().encode()
    except OSError:
        print('Unable to read client_keys')

    print(f'Key for client: {KEY_AS}')
    KEY_AS_SUITE = Fernet(KEY_AS)
    # enc = KEY_AS_SUITE.encrypt('abc'.encode())
    # dec = KEY_AS_SUITE.decrypt(enc).decode()
    # print(dec)


if __name__ == '__main__':
    client_offset = 0

    if len(sys.argv) == 2:
        try:
            client_offset = int(sys.argv[1])
        except ValueError:
            print('Supply a valid client offset')
            exit()

    try:
        set_client_key(client_offset % 10)
        update_fileservers()
        while True:
            cli()
    except KeyboardInterrupt:
        print('Client terminated')
