import re
from pathlib import Path

import sys

import secrets

from xmlrpc.client import ServerProxy

from cryptography.fernet import Fernet

from utils.reply import Reply
from utils.config import URI, COORDINATOR_LOCATION
from utils.fernet_helper import encode_data, decode_data
from utils.logger import Logger


COORDINATOR = ServerProxy(COORDINATOR_LOCATION)
FILESERVERS = list()
ACTIVE_FILESERVER = None
ROOT = Path('/')
ACTIVE_DIRECTORY = ROOT
ACTIVE_PORT = 0
LOG = Logger()

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
    LOG.log(f'Active port: {ACTIVE_PORT}')


def is_mount_point_root() -> bool:
    global ACTIVE_DIRECTORY
    return ACTIVE_DIRECTORY == ROOT


def update_fileservers():
    global FILESERVERS
    FILESERVERS = COORDINATOR.get_fs()


def verify_nonce(sent_nonce: int, received_nonce: str) -> bool:
    # print(f'sent: {sent_nonce}, recv: {received_nonce}')
    try:
        received_nonce = int(received_nonce)
    except TypeError:
        print('Nonce is NaN')
    finally:
        return sent_nonce == received_nonce


def verify_nonce_handler(sent_nonce: int, received_nonce: str, is_coord: bool = False):
    b = 'coordinator' if is_coord else 'client'
    if verify_nonce(sent_nonce, received_nonce) is True:
        print(f'Nonce verified for client/{b} phase')
    else:
        print(f'Nonce not verified for client/{b} phase')
        print('Imposter detected')
        print('Venting')
        exit()


def get_session_key(nonce=42):
    global OFFSET_A
    global ACTIVE_PORT
    if ACTIVE_PORT == 0:
        print('No active server')
        return
    nonce = secrets.randbelow(100)

    ses = COORDINATOR.get_enc_session_key(OFFSET_A, ACTIVE_PORT, nonce)
    ses = dict(ses)

    for_client = ses['for_a']
    port_b_recv = for_client['port_b']
    ses_key_recv = for_client['key_ab']
    nonce_recv = for_client['nonce']

    ses_key = KEY_AS_SUITE.decrypt(encode_data(ses_key_recv)).decode()
    port_b = KEY_AS_SUITE.decrypt(encode_data(port_b_recv)).decode()
    nonce_dec = KEY_AS_SUITE.decrypt(encode_data(nonce_recv)).decode()

    verify_nonce_handler(nonce, nonce_dec, True)

    print(f'Session key (Kab): {ses_key}')

    for_fs = ses['for_b']
    # print(ses)
    return (ses_key, for_fs)


# def encrypt_for_ses()
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
                (ses_key, enc_ses_key) = get_session_key()
                ses_suite = Fernet(ses_key)
                file_1 = ses_suite.encrypt(encode_data(tokens[1]))
                file_2 = ses_suite.encrypt(encode_data(tokens[2]))
                nonce2 = secrets.randbelow(100)
                nonce_enc = ses_suite.encrypt(encode_data(nonce2))

                resp = ACTIVE_FILESERVER.copy_file(file_1, file_2, nonce_enc, enc_ses_key)

                msg_enc = resp['message']
                nonce_recv_enc = resp['nonce']
                msg = ses_suite.decrypt(encode_data(msg_enc)).decode()
                nonce_recv = ses_suite.decrypt(encode_data(nonce_recv_enc)).decode()

                verify_nonce_handler(nonce2, nonce_recv)

                print(msg)
                # print(ACTIVE_FILESERVER.copy_file(tokens[1], tokens[2])['message'])

            elif cmd == 'cat' and ACTIVE_FILESERVER:
                (ses_key, enc_ses_key) = get_session_key()
                ses_suite = Fernet(ses_key)
                file_arg = ses_suite.encrypt(encode_data(tokens[1]))
                nonce2 = secrets.randbelow(100)
                nonce_enc = ses_suite.encrypt(encode_data(nonce2))

                resp = ACTIVE_FILESERVER.cat(file_arg, nonce_enc, enc_ses_key)
                # nonce_recv = resp['nonce']
                nonce_recv_enc = resp['nonce']
                nonce_recv = ses_suite.decrypt(encode_data(nonce_recv_enc)).decode()

                verify_nonce_handler(nonce2, nonce_recv)

                # resp = dict(ACTIVE_FILESERVER.cat(tokens[1]))
                if resp['success'] is True:
                    dec_data = resp['data']
                    dec_data = ses_suite.decrypt(encode_data(dec_data)).decode()
                    print(dec_data)
                else:
                    dec_msg = resp['message']
                    dec_msg = ses_suite.decrypt(encode_data(dec_msg)).decode()
                    print(dec_msg)

            elif cmd == 'cd':
                change_active_fileserver(tokens[1])

            elif cmd == 'exit':
                exit()

            elif cmd == 'test':
                (ses_key, enc_ses_key) = get_session_key()
                ses_suite = Fernet(ses_key)
                payload_arg = ses_suite.encrypt(encode_data(tokens[1]))
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
        while True:
            cli()
    except KeyboardInterrupt:
        print('Client terminated')
