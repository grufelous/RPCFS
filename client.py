import re
from pathlib import Path

from xmlrpc.client import ServerProxy

from utils.reply import Reply
from utils.config import URI, COORDINATOR_LOCATION


COORDINATOR = ServerProxy(COORDINATOR_LOCATION)
FILESERVERS = list()
ACTIVE_FILESERVER = None
ROOT = Path('/')
ACTIVE_DIRECTORY = ROOT

supported_commands = {
    'pwd': 0,
    'ls': 0,
    'cp': 2,
    'cat': 1,
    'help': 0,
    'cd': 1,
    'exit': 0,
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
    path = Path(dir)
    if ACTIVE_FILESERVER is not None and path == Path('..'):
        ACTIVE_FILESERVER = None
        ACTIVE_DIRECTORY = ROOT
    else:
        port = get_port_from_friendly_name(str(path))
        if port in FILESERVERS:
            ACTIVE_FILESERVER = ServerProxy(f'{URI}:{port}')
            ACTIVE_DIRECTORY = Path(get_friendly_name(port))


def is_mount_point_root() -> bool:
    global ACTIVE_DIRECTORY
    return ACTIVE_DIRECTORY == ROOT


def update_fileservers():
    global FILESERVERS
    FILESERVERS = COORDINATOR.get_fs()


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


if __name__ == '__main__':
    try:
        while True:
            cli()
    except KeyboardInterrupt:
        print('Client terminated')
